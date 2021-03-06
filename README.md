# Casters


Program caster.py for command line management of 
couchdb design documents 

Extracted out of scripts from social farm project at 
https://github.com/SocialFarm


# Installation 


Download the script and resources somewhere in your 
filesystem.  Make the script available in your executable path.  

For example do the following in /usr/local/bin:  

   ln -s /some/path/caster.py 


# Usage 

Create a design document skeleton structure 

    caster.py [-d dirname] generate  

Push/pull a given design document's code to/from a couchdb 
 
    caster.py [-d dirname] pull couchdburl 

    caster.py [-d dirname] push couchdburl 

For example:
 
    caster.py -d ./testdesign pull http://usr:pwd@localhost:5984/testdb/_design/testdesign


## Test cases 

Creates view directory along with i) a running example test case, ii) a 
running sample library file which works through the common js modules
(http://wiki.apache.org/couchdb/CommonJS_Modules), and iii) and a test harness 
to enforce identical execution of the map and reduce functions whether 
they execute on couchdb or on local system with user inspection/control.  

You can safely delete the example/sample files (eg: in lib or tests 
directory) 

Also note that -f will overwrite existing view on local directory.  

    caster.py [-d dirname] [-f] create view name


Run either a single view test cases or all the test cases in all the views 
  
    caster.py [-d dirname] test view name

    caster.py [-d dirname] test


In general you can always go to the tests directory below the view directory and 
manually run the tests explicitly eg: js testExample.js  

This feature can be used to for example profile your map or reduce function, eg 
using the xpc shell javascript interpreter: https://developer.mozilla.org/en-US/docs/Mozilla/XPConnect/xpcshell/Profiling

Similarly, one can interactively debug the execution of map/reduce functions with the visual 
rhino debugger: https://developer.mozilla.org/en-US/docs/Rhino/Debugger



## Dependencies 
couchdb-python : https://pypi.python.org/pypi/CouchDB
python : tested with 2.7 , but should work a for a few older versions too. 


## To be implemented 
caster.py [-d dirname] test [show|list|update|filters] name

caster.py [-d dirname] create [show|list|update|filters] name

caster.py [-d dirname] delete [view|show|list|update|filters] name






# Directory stucture 

    designname/   (could be any dir though - design doc name seems safer)  

        _attachments/   (can have directory tree within here)

        views/
            lib/
            viewname1/
                map.js
                reduce.js
        shows
            show.js

        lists/ 
            listxxx.js

        updates/
            funcname.js

        filters/
            funcname.js 

        validate_doc_update.js






# Goals for maintaining code in couchdb (views/lists/etc)
  - identical code on couchdb and local fs (eg: no include code through
    comment as in couchapp)
  - support common code includes consistent with couchdb through the
    "requires" construct 
  - this "identical code" can be run through tools like unit testing 
    framework,  debugger, and profiler - and can be better tracked through
    version control tools.

## Additionally, the standard goals (supported by other tools)
  - push your code to couchdb (TODO : skip push if identical) 
  - pull code from couchdb 
  - maintain any attachments - the attachment files should ideally
    be openable through browser on local system and relative 
    links should also work










# Relevant external information 

## Tuning javascript code 
Javascript code used in map and reduce functions of couchdb 
is hard to properly tune while loaded in couchdb 

One way to improve code performance is to run the code 
locally and time through js, eg: 

    js -b test.js



## Readings and relevant links

http://wiki.apache.org/couchdb/JavascriptPatternViewCommonJs

http://wiki.apache.org/couchdb/CommonJS_Modules

https://developer.mozilla.org/en-US/docs/Mozilla/Projects/SpiderMonkey?redirectlocale=en-US&redirectslug=SpiderMonkey

https://github.com/WebReflection/wru

