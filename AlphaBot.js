/* Extension demonstrating a blocking command block */
/* Sayamindu Dasgupta <sayamindu@media.mit.edu>, May 2014 */


new (function() {
    var ext = this;
	var URL = 'http://192.168.2.141:9999'

    // Cleanup function when the extension is unloaded
    ext._shutdown = function() {};

    // Status reporting code
    // Use this to report missing hardware, plugin or unsupported browser
    ext._getStatus = function() {
        return {status: 2, msg: 'Ready'};
    };

    // Functions for block with type 'w' will get a callback function as the 
    // final argument. This should be called to indicate that the block can
    // stop waiting.
    ext.wait_random = function(callback) {
        wait = Math.random();
        console.log('1Waiting for ' + wait + ' seconds');
        window.setTimeout(function() {
            callback();
        }, wait*1000);
    };

	// AlphaBot Motor 
	// 
	//
	ext.AlphaBot_motor = function(callback) {
        
		$.post(URL +'/AlphaBot/motor', {
        left: 11,
        right: 10
		}, function(result){
			console.log(result);
			
			//var obj = JSON.parse(result);
			for (var key in result) {
				console.log("[ " + key + " ] = " + result[key] ); // "User john is #234"
				callback();
			}	
		});
		
        console.log('Execute AlphaBot move.');
        
    };
	
	ext.AlphaBot_motor_1 = function(v_left, v_right) {
        
		$.post( URL+ '/AlphaBot/motor', {
        left: v_left,
        right: v_right
		}, function(result){
			console.log(result);
			//var obj = JSON.parse(result);
			for (var key in result) {
				console.log("no sync [ " + key + " ] = " + result[key] ); // 
				//callback();
			}	
		});
		
        console.log('Execute AlphaBot move.');
        
    };
	
	
	ext.AlphaBot_motor_d = function(direction) {
		speed=50
        if (direction=='forward'){
			v_left=speed;
			v_right=speed;
		}else if(direction=='backward'){
			v_left=-speed;
			v_right=-speed;
		}else if(direction=='left'){
			v_left=speed;
			v_right=0;
		}else if(direction=='right'){
			v_left=0;
			v_right=speed;
		}else if(direction=='spin_r'){
			v_left=-speed;
			v_right=speed;
		}else if(direction=='spin_l'){
			v_left=speed;
			v_right=-speed;
		}else {  //STOP
			v_left=0;
			v_right=0;
		}
		
		$.post( URL+ '/AlphaBot/motor', {
        left: v_left,
        right: v_right
		}, function(result){
			console.log(result);
			//var obj = JSON.parse(result);
			for (var key in result) {
				console.log("no sync [ " + key + " ] = " + result[key] ); // 
				//callback();
			}	
		});
		
        console.log('Execute AlphaBot move.');
        
    };
	
    // Block and block menu descriptions
    var descriptor = {
        blocks: [
            //['w', 'wait for random time', 'wait_random'],
			//['w', 'Move AlphaBot with speed', 'AlphaBot_motor'],
			[' ', 'set motor speed left[-100:100]:%n - right[-100:100]:%n', 'AlphaBot_motor_1',50,50],
			[' ', 'Move AlphaBot %m.motorDir', 'AlphaBot_motor_d','stop']
        ],
		menus: {
			motorSpeed: ['255', '100', '50', '0', '-100', '-255'],
			motorDir: ['forward', 'backward', 'left', 'right', 'stop','spin_l', 'spin_r'],
			
		},
			url: 'http://info.scratch.mit.edu/WeDo'
		};

    // Register the extension
    ScratchExtensions.register('Random wait extension', descriptor, ext);
})();