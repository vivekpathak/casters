#!/usr/bin/env python 

# Pull a design document from couchdb and store it in
# the canonical local directory structure

# Author : vpathak 
# Copyright 2009-2013
# License : Apache (see in repository at https://github.com/SocialFarm/SocialFarm/blob/master/LICENSE.txt)

import os, sys, getopt, re, time, mimetypes
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
                filename = "%s/%s.js" % (destdir, funcname) 
                open( filename, "w" ).write( funcobj[funcname] )
            else:
                self._pull_r( "%s/%s" % (destdir, funcname), funcobj[funcname] , i + 1 )

    def _pull_attachments(self):         
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
        
    # recursively visit all the files and get their text into ddoc
    def _push_r(self, currdir, keylist, ddoc) :     
        for name in os.listdir(currdir): 
            if os.path.isdir(os.path.join(currdir, name)):
                if name == "_attachments" :
                    return 
                print "found dir %s in %s" % (name, currdir)
                self._push_r(os.path.join(currdir, name), keylist + [name], ddoc)
            else : 
                print "found non dir %s in %s" % (name, currdir)
                pos = name.find('.') 
                if pos != -1 : 
                    keyname = name[:pos]
                else:
                    keyname = name 
                self._merge_updates( ddoc, keylist + [keyname], 
                                     open( os.path.join(currdir, name) ).read() ) 
        #print ddoc 
        
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
    "views", "views/lib" ,
    "shows",
    "lists",
    "updates",
    "filters"
    ]

    files = [
    ("validate_doc_update.js" ,'''// sample generated by caster.
// see http://wiki.apache.org/couchdb/Document_Update_Validation  
function(newDoc, oldDoc, userCtx, secObj) {
  // eg: throw( {forbidden: 'detailed message'} ) ; // or throw( {unauthorized: '...'} ) ;
}
''') ,
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



        

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:] , 'hd:' , ["help","directory"])
    except getopt.GetoptError, err:
        print str(err) 
        _usage()

    working_directory = os.getcwd() 
    for o, a in opts:
        if o in ("--help" , "-h" ) :
            _usage()
        if o in ("--directory" , "-d" ) :
            print "Setting working directory " , a
            time.sleep(2) 
            working_directory = a 

            
    if len(args) == 1 and args[0] == "generate" :
        _generate(working_directory)
    elif len(args) == 2 :
        url = args[1]
        caster = Caster( working_directory , url )    
        if args[0] == "push" :
            caster.push()
        elif args[0] == "pull" :
            caster.pull()
        else:
            _usage()
    else:
        _usage()

    print "Done"    
    sys.exit(0)    
    


    # TODO : have force flag 
    # if the server doesnt have the db, create it  

    
    


