// sample generated by caster.py : https://github.com/vivekpathak/casters
// modify/adapt/copy as needed

function fibo(a) {
    if( a < 0 ) { 
        return undefined ; 
    }
    else if( a == 0 ) { 
        return 0; 
    } 
    else if (a == 1) {
        return 1;
    } 
    else {
        return fibo(a - 1) + fibo(a - 2);
    }
}

exports.fibo = fibo;