# Casters


Standalone program caster.py for command line management of 
couchdb design documents 

Extracted out of scripts from social farm project at 
https://github.com/SocialFarm



# Usage 

Make the script available in your executable path.  For example
in /usr/local/bin:  ln -s /some/path/caster.py ; or just copy 
the script into path.  

caster generate [dirname] 

caster pull couchdburl 

caster push couchdburl 

## Dependencies 
couchdb-python : https://pypi.python.org/pypi/CouchDB


## To be implemented 
caster test 

caster create [view|show|list|update] name

caster delete [view|show|list|update] name






# Directory stucture 

    designname/   (could be any dir though - design doc name seems safer)  

        _attachments/ 

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

