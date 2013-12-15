


function ExampleStatisticsCls() { 
    this.values = [] ; 
    
    this.addValue = function (x) { 
        this.values.push( 0 + x ) ; 
    }

    this.getAverage = function() {
        var sum = 0;
        for( var i = 0; i < this.values.length; i++ ) { 
            sum += this.values[i] ; 
        }
        
        if( this.values.length > 0 ) { 
            sum = sum / this.values.length ;
        }
        return sum;
    }
}