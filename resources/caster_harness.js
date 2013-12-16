// auto-generated by caster.py : https://github.com/vivekpathak/casters
// do not edit. consider improving the script on github instead

// define globals to be accessed by test cases 
var keys = [] ;
var values = [] ;
var map = null ; 
var reduce = null ;

// define functions that map the functions defined 
// in couchdb execution context to something meaningful for 
// the test case 

function emit(k, v) {
   keys.push(k)  ;
   values.push(v) ;
}


function sum(values) { 
   var total = 0;
   for( var i = 0; i < values.length; i++ ){
     total += values[i] ;
   }
   return total ; 
}


function require(name) {
   // we are currently in test dir, i.e. ../ is view; ../../ is views; and ../../../ is design doc root
   print( "loading requires code from \"../../../" + name + "\"" ) ; 
   eval( "var exports = {}; eval(read(\"../../../" + name + "\"));" ) ; 
   return exports ; 
}


function log(mesg) { 
   print(mesg) ;
}


// load the map and reduce code into execution context 
function _load_map_reduce() { 
   var mapcode;
   var reducecode;

   mapcode = read("../map.js");
   eval("map = " + mapcode ) ;

   try {
      reducecode = read("../reduce.js");
      eval(" reduce = " + reducecode ) ;
   } catch(x) {
      print ("Did not find reduce function" )  ;
   }
}


_load_map_reduce() ;
print( "loaded test harness" ) ;
