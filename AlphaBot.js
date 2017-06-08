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
    /*ext.wait_random = function(callback) {
        wait = Math.random();
        console.log('1Waiting for ' + wait + ' seconds');
        window.setTimeout(function() {
            callback();
        }, wait*1000);
    };*/

	// AlphaBot Motor 
	// 
	//
	
	//Ne koristi se više
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
	
	
	// 
	// AlphaBot Infrared sensor
	//
	ext.AlphaBot_InfraRed = function(side) {
        var ret_d=false;
		
		jQuery.ajax({
		type: "POST",
        url:   URL +'/AlphaBot/infrared',
        success: function(result){
			console.log(result);
			if (side =='left'){
				ret_d = result['left'];
			}else{ //right
				ret_d = result['right'];
			}
		},
         async:   false
		}); 
        console.log('Execute AlphaBot infrared.');
        return ret_d;
    };
	
	// 
	// AlphaBot Infrared Line Tracker
	//
	ext.AlphaBot_LT_calibrate = function() {
        
		jQuery.ajax({
		type: "POST",
        url:   URL +'/AlphaBot/lt_calibrate',
        success: function(result){
			
		},
         async:   false
		}); 
        console.log('Execute AlphaBot Calibrate Line Tracker.');
    };
	
	ext.AlphaBot_LT_Read = function() {
        
		jQuery.ajax({
		type: "POST",
        url:   URL +'/AlphaBot/lt_read',
        success: function(result){
			console.log(result);
			return result['value'];
		},
         async:   false
		}); 
        console.log('Execute AlphaBot Line Tracker Get Value.');
        
    };
	
	ext.AlphaBot_motorcount = function(side) {
        var ret_val;
		jQuery.ajax({
		type: "POST",
        url:   URL +'/AlphaBot/motorcount',
        success: function(result){
			console.log(result);
			if (side=='left'){
				ret_val = result['left'];
			}else{
				ret_val = result['right'];
			}
		},
         async:   false
		}); 
		
        console.log('Execute AlphaBot Get Motor Count.');
		console.log(ret_val);
        return ret_val;
    };
    // Block and block menu descriptions
    var descriptor = {
        blocks: [
            //['w', 'wait for random time', 'wait_random'],
			[' ', 'set motor speed left[-100:100]:%n - right[-100:100]:%n', 'AlphaBot_motor_1',50,50],
			[' ', 'move AlphaBot %m.motorDir', 'AlphaBot_motor_d','stop'],
			['b', 'get Infrared sensor %m.side', 'AlphaBot_InfraRed','left'],
			[' ', 'calibrate Infrared LineTracker', 'AlphaBot_LT_calibrate'],
			['r', 'get Infrared LineTracker', 'AlphaBot_LT_Read'],
			['r', 'get motor counter %m.side', 'AlphaBot_motorcount'],
        ],
		menus: {
			motorSpeed: ['255', '100', '50', '0', '-100', '-255'],
			motorDir: ['forward', 'backward', 'left', 'right', 'stop','spin_l', 'spin_r'],
			side: ['left', 'right'],
			
		},
			url: 'http://info.scratch.mit.edu/WeDo'
		};

    // Register the extension
    ScratchExtensions.register('AlphaBot extension', descriptor, ext);
})();