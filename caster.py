#!/usr/bin/env python 

# Program for command line management of couchdb design documents 
# Author : Vivek Pathak  
# Copyright 2009-2013
# License : Apache 2 
# Extracted and modified from scripts in https://github.com/SocialFarm/

import os, sys, getopt, re, time, mimetypes, glob, subprocess
from couchdb.client import Database, Server 

def _usage(errorMessage = None) :
    if errorMessage:
        print "\n\tError : %s\n" % errorMessage 
    print 'Usage : %s --help|-h' % sys.argv[0] 
    print '        %s <push|pull> <couchdburl> [-d <dir to work>]' % sys.argv[0]
    print '        %s <generate> [-d <dir to work>]' % sys.argv[0]  
    print 'eg:\n\t%s pull http://usr:pwd@localhost:5984/testdb/_design/testdesign' % sys.argv[0]  
    sys.exit(-1) 



def make_dir(dirname) :
    try :
        os.makedirs( dirname )
    except OSError, e:
        if "exists" not in e.strerror:
            raise(e)



class Caster(object) : 

    def __init__(self, basedir, url) : 
        self.basedir = basedir 
        self.language = "javascript" 

        # parse out the design document id, etc
        regex = re.compile( r'(.*)/([^\s/]*)/(_design/[^\s/]*)/?$' )
        match = regex.match( url )
        if match is None:
            _usage("no match on url of design document")

        (self.couchurl, self.dbname, self.designdoc) = [ match.group(i) for i in [1,2,3] ]

        self.server = Server(self.couchurl)
        if self.dbname not in self.server:
            _usage( "dbname %d doesnt exist in database %s" % (self.dbname, self.couchurl) ) 
    
        self.db = self.server[self.dbname]

        if self.designdoc in self.db:
            self.ddoc = self.db[ self.designdoc ] 
        else :
            self.ddoc = { "language" : "javascript" } 
        #print self.ddoc


 


    def pull(self) :
        if len(self.ddoc.keys()) == 0 : 
            _usage( "Design document doesnt exist or has no data; can not pull" ) 
        targetdir = self.basedir 
        ddoc = self.ddoc
        for k in ddoc.keys():
            if k in [ "_id" , "_rev" ] : 
                pass
            elif k in ["_attachments"] : 
                pass
            else :
                self._pull_r( "%s/%s" % (targetdir, k) , ddoc[k] , 0 )
        self._pull_attachments() 
                
    def _pull_r(self, destdir, funcobj , i ) :
        if type(funcobj) is str :
            destname = destdir.split('/')[-1]
            if destname == "validate_doc_update" : 
                filename = "%s/%s.js" % (os.path.abspath(os.path.join(destdir, '..')), destname) 
                open( filename, "w" ).write( funcobj )
            else:
                # skipping things like language etc
                pass 
            return 
        make_dir(destdir)
        for funcname in funcobj:
            print "working on %s %s" % (destdir, funcname)
            if type(funcobj[funcname]) is str :
                # maintain extension if it already has one
                if funcname.find(".") == -1: 
                    filename = "%s/%s.js" % (destdir, funcname)
                else:
                    filename = "%s/%s" % (destdir, funcname) 
                open( filename, "w" ).write( funcobj[funcname] )
            else:
                self._pull_r( "%s/%s" % (destdir, funcname), funcobj[funcname] , i + 1 )

    def _pull_attachments(self):
        if "_attachments" not in self.ddoc: 
            return 
        for aname in self.ddoc[ "_attachments" ]:
            filepath = self.basedir + "/_attachments/" + aname
            print "Pulling ", filepath
            make_dir( os.path.split( filepath )[0] ) 
            wfd = open( filepath , "w" )
            rfd = self.db.get_attachment(self.ddoc, aname)
            if rfd is not None:
                wfd.write( rfd.read() )
                print "done " , aname 



    def push(self) :
        targetdir = self.basedir 
        ddoc = self.ddoc
        self._push_r(targetdir, [], ddoc)
        self.db[self.designdoc] = ddoc
        self._push_attachments()
        
    # recursively visit all the files and get their content into ddoc
    def _push_r(self, currdir, keylist, ddoc) :     
        for name in os.listdir(currdir): 
            if os.path.isdir(os.path.join(currdir, name)):
                if name == "_attachments" :
                    return 
                print "found dir %s in %s" % (name, currdir)
                self._push_r(os.path.join(currdir, name), keylist + [name], ddoc)
            else : 
                print "found non dir %s in %s" % (name, currdir)
                # if this is couchdb file then strip extension, else send as is since keys are
                # allowed to have '.'
                keyname = self._get_keyname_with_optional_extension( name , currdir ) 
                self._merge_updates( ddoc, keylist + [keyname], 
                                     open( os.path.join(currdir, name) ).read() ) 
        #print ddoc
                
    def _get_keyname_with_optional_extension(self, name , currdir ) :
        pos = name.find('.') 
        if pos != -1 :
            pathlst = currdir.split('/')
            if len(pathlst) >= 2 and pathlst[-2] == "views" and pathlst[-1] != "lib" :  
                return name[:pos]
            elif len(pathlst) >= 1 and pathlst[-1] in ["shows" , "lists" , "updates" , "filters"] :
                return name[:pos]
            elif name == "validate_doc_update.js" :
                return name[:pos]
        return name 

    def _get_recursive_dict(self, keylist , data ) :
        if keylist == []:
            return data
        else:
            return {keylist[0] : self._get_recursive_dict(keylist[1:], data) }

    def _merge_updates(self, obj, fldkeys, data):
        res = obj
        curr = res
        n = len(fldkeys)
        for i in range(0,n):
            k = fldkeys[i]
            # no key, get the remaining dicts directly 
            if k not in curr:
                curr[k] = self._get_recursive_dict( fldkeys[i+1:] , data )
                return res
            # last key, overwrite the data 
            if i == (n-1):
                if len(data) > 0:
                    curr[k] = data
                else:
                    del curr[k]
                break
            # another iteration 
            curr = curr[k]

        return res
    
    def _push_attachments(self) :
        for dirpath, dirnames, filenames in os.walk(self.basedir + "/_attachments/"):
            for f in filenames:
                relpath = os.path.relpath("%s/%s"% (dirpath, f) , self.basedir + "/_attachments/" )
                filename = "%s/%s" % (dirpath, f)
                print "Sending attachment from file %s to _attachments/%s" % (filename, relpath)        
                data = open(filename).read()
                self.db.put_attachment( self.ddoc, data, relpath,
                                        content_type=mimetypes.guess_type(relpath)[0] )
    


def _generate(dirname) :
    dirs = [
    "_attachments" ,
    "views",
    "views/lib",
    "shows",
    "lists",
    "updates",
    "filters"
    ]
    files = [
    ("validate_doc_update.js" , _get_resource("validate_doc_update.js")) ,
    ("views/lib/libSlowFiboExample.js" , _get_resource("libSlowFiboExample.js")),
    ]
    make_dir(dirname)
    # make template directories
    for d in dirs:
        make_dir(dirname + "/" + d )
        print "created directory " + dirname + "/" + d  
    # write out template files
    for (filename, code) in files:
        fd = open( dirname + "/" + filename, "w")
        fd.write(code)
        print "created file " + dirname + "/" + filename





def _generate_view_with_testcase(viewdirname, use_force) :
    if not use_force and os.path.isdir(viewdirname) :
        print "view at " , viewdirname , " already exists, giving up"
        return 
    make_dir( viewdirname + "/tests" )
    # TODO : harness to include library require includes
    open( viewdirname + "/tests/caster_harness.js", "w").write( _get_resource("caster_harness.js"))
    open( viewdirname + "/tests/testExample.js", "w").write(_get_resource("testExample.js"))
    open( viewdirname + "/map.js" , "w" ).write(_get_resource("map.js"))
    print "created test harness, example test case, and map.js in view directory %s" % viewdirname 



def _get_resource(resname):
    resource_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')  # todo : this is too common!
    return open( resource_directory + "/" + resname ).read()



def _run_test_cases(viewdirname):
    for test in glob.glob( viewdirname + "/tests/*test*.js" ) :
        (dirpath, testfile) = os.path.split( test )
        print "About to run test '%s' in directory %s " % (testfile, dirpath)  
        proc = subprocess.Popen(["js", testfile] , cwd=dirpath)
        if proc.wait() != 0 :
            print "Test failed"
            sys.exit(2)
        else:
            print "Passed test '%s' in directory %s " % (testfile, dirpath) 


def _test_all(working_directory):
    for viewdir in glob.glob( working_directory + "/views/*" ):
        print viewdir
        if os.path.isdir(viewdir):
            _run_test_cases(viewdir) 



if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:] , 'fhd:' , ["help","directory"])
    except getopt.GetoptError, err:
        print str(err) 
        _usage()

    use_force = False 
    working_directory = os.getcwd() 
    for o, a in opts:
        if o in ("--help" , "-h" ) :
            _usage()
        if o in ("--force", "-f" ) :
            use_force = True
        if o in ("--directory" , "-d" ) :
            print "Setting working directory " , a
            time.sleep(2) 
            working_directory = a 

            
    if len(args) == 1 and args[0] == "generate" :
        _generate(working_directory)
    elif len(args) == 1 and args[0] == "test" :
        _test_all(working_directory)
    elif len(args) == 2 :
        url = args[1]
        caster = Caster( working_directory , url )    
        if args[0] == "push" :
            caster.push()
        elif args[0] == "pull" :
            caster.pull()
        else:
            _usage()
    elif len(args) == 3:
        if args[0] == "create" and args[1] == "view" :
            _generate_view_with_testcase( working_directory + "/views/" + args[2],  use_force)
        elif args[0] == "test" and args[1] == "view" :
            _run_test_cases(working_directory + "/views/" + args[2]) 
        else:
            _usage()
    else:
        _usage()

    print "Done"    
    sys.exit(0)    
    


    # TODO : have force flag 
    # if the server doesnt have the db, create it  

    
    


