import RPi.GPIO as GPIO
import time

class AlphaBot(object):

	counter_left=0
	counter_right=0
	counter_inc_l=0
	counter_inc_r=0
	counter_ena_l=0
	counter_ena_r=0
	
	def __init__(self,in1=12,in2=13,ena=6,in3=20,in4=21,enb=26,dr=16, dl = 19):

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
	
		#############
		#INIT Motor speed
		#############
		GPIO.setup(8, GPIO.IN)  
		GPIO.setup(7, GPIO.IN) 
		
		#############
		#INIT Motor setup
		#############
		self.IN1 = in1
		self.IN2 = in2
		self.IN3 = in3
		self.IN4 = in4
		self.ENA = ena
		self.ENB = enb
		GPIO.setup(self.IN1,GPIO.OUT)
		GPIO.setup(self.IN2,GPIO.OUT)
		GPIO.setup(self.IN3,GPIO.OUT)
		GPIO.setup(self.IN4,GPIO.OUT)
		GPIO.setup(self.ENA,GPIO.OUT)
		GPIO.setup(self.ENB,GPIO.OUT)
		self.forward()
		self.PWMA = GPIO.PWM(self.ENA,500)
		self.PWMB = GPIO.PWM(self.ENB,500)
		self.PWMA.start(50)
		self.PWMB.start(50)
		
		###############################
		# INIT Infrared sensor Left - Right
		###############################
		self.DR = dr
		self.DL = dl
		GPIO.setup(self.DR,GPIO.IN,GPIO.PUD_UP)
		GPIO.setup(self.DL,GPIO.IN,GPIO.PUD_UP)
	
		###############################
		# INIT Infrared Line Tracker
		###############################
		self.numSensors = 5
		self.calibratedMin = [0] * self.numSensors
		self.calibratedMax = [1023] * self.numSensors
		self.last_value = 0
		self.LT_CS = 5
		self.LT_Clock = 25
		self.LT_Address = 24
		self.LT_DataOut = 23
		GPIO.setup(self.LT_Clock,GPIO.OUT)
		GPIO.setup(self.LT_Address,GPIO.OUT)
		GPIO.setup(self.LT_CS,GPIO.OUT)
		GPIO.setup(self.LT_DataOut,GPIO.IN,GPIO.PUD_UP)
		
	###############################
	# Methodes Infrared speed sensor
	###############################	
	
	def USD_Int_Handler_Left(self, channel):
		self.counter_left = self.counter_left +self.counter_inc_l
	def USD_Int_Handler_Right(self, channel):
		self.counter_right = self.counter_right +self.counter_inc_r
	def USD_enableInterupt_L(self):
		if (self.counter_ena_l==0):
			GPIO.add_event_detect(8, GPIO.RISING, callback=self.USD_Int_Handler_Left)  
			self.counter_ena_l=1
	def USD_enableInterupt_R(self):
		if (self.counter_ena_r==0):
			GPIO.add_event_detect(7, GPIO.RISING, callback=self.USD_Int_Handler_Right)  
			self.counter_ena_r=1
	def USD_disableInterupt_L(self):
		GPIO.remove_event_detect(8)
	def USD_disableInterupt_R(self):
		GPIO.remove_event_detect(7)
		
	def USD_GetSpeedCounter(self):
		return self.counter_left, self.counter_right
	
	def USD_ResetSpeedCounter(self):
		self.counter_left = 0  
		self.counter_right = 0
		
	###############################
	# Methodes Infrared sensor Left - Right
	###############################
	"""
	Reads the sensor values into an array. There *MUST* be space
	for as many values as there were sensors specified in the constructor.
	Example usage:
	unsigned int sensor_values[8];
	sensors.read(sensor_values);
	The values returned are a measure of the reflectance in abstract units,
	with higher values corresponding to lower reflectance (e.g. a black
	surface or a void).
	"""
	def LT_AnalogRead(self):
		value = [0,0,0,0,0,0]
		#Read Channel0~channel4 AD value
		for j in range(0,6):
			GPIO.output(self.LT_CS, GPIO.LOW)
			for i in range(0,4):
				#sent 4-bit Address
				if(((j) >> (3 - i)) & 0x01):
					GPIO.output(self.LT_Address,GPIO.HIGH)
				else:
					GPIO.output(self.LT_Address,GPIO.LOW)
				#read MSB 4-bit data
				value[j] <<= 1
				if(GPIO.input(self.LT_DataOut)):
					value[j] |= 0x01
				GPIO.output(self.LT_Clock,GPIO.HIGH)
				GPIO.output(self.LT_Clock,GPIO.LOW)
			for i in range(0,6):
				#read LSB 8-bit data
				value[j] <<= 1
				if(GPIO.input(self.LT_DataOut)):
					value[j] |= 0x01
				GPIO.output(self.LT_Clock,GPIO.HIGH)
				GPIO.output(self.LT_Clock,GPIO.LOW)
			#no mean ,just delay
			for i in range(0,6):
				GPIO.output(self.LT_Clock,GPIO.HIGH)
				GPIO.output(self.LT_Clock,GPIO.LOW)
#			time.sleep(0.0001)
			GPIO.output(self.LT_CS,GPIO.HIGH)
		return value[1:]
		
	"""
	Reads the sensors 10 times and uses the results for
	calibration.  The sensor values are not returned; instead, the
	maximum and minimum values found over time are stored internally
	and used for the readCalibrated() method.
	"""
	def LT_calibrate(self):
		max_sensor_values = [0]*self.numSensors
		min_sensor_values = [0]*self.numSensors
		for j in range(0,10):
		
			sensor_values = self.LT_AnalogRead();
			
			for i in range(0,self.numSensors):
			
				# set the max we found THIS time
				if((j == 0) or max_sensor_values[i] < sensor_values[i]):
					max_sensor_values[i] = sensor_values[i]

				# set the min we found THIS time
				if((j == 0) or min_sensor_values[i] > sensor_values[i]):
					min_sensor_values[i] = sensor_values[i]

		# record the min and max calibration values
		for i in range(0,self.numSensors):
			if(min_sensor_values[i] > self.calibratedMin[i]):
				self.calibratedMin[i] = min_sensor_values[i]
			if(max_sensor_values[i] < self.calibratedMax[i]):
				self.calibratedMax[i] = max_sensor_values[i]

	"""
	Returns values calibrated to a value between 0 and 1000, where
	0 corresponds to the minimum value read by calibrate() and 1000
	corresponds to the maximum value.  Calibration values are
	stored separately for each sensor, so that differences in the
	sensors are accounted for automatically.
	"""
	def	LT_readCalibrated(self):
		value = 0
		#read the needed values
		sensor_values = self.LT_AnalogRead();

		for i in range (0,self.numSensors):

			denominator = self.calibratedMax[i] - self.calibratedMin[i]

			if(denominator != 0):
				value = (sensor_values[i] - self.calibratedMin[i])* 1000 / denominator
				
			if(value < 0):
				value = 0
			elif(value > 1000):
				value = 1000
				
			sensor_values[i] = value
		
		print("readCalibrated",sensor_values)
		return sensor_values
			
	"""
	Operates the same as read calibrated, but also returns an
	estimated position of the robot with respect to a line. The
	estimate is made using a weighted average of the sensor indices
	multiplied by 1000, so that a return value of 0 indicates that
	the line is directly below sensor 0, a return value of 1000
	indicates that the line is directly below sensor 1, 2000
	indicates that it's below sensor 2000, etc.  Intermediate
	values indicate that the line is between two sensors.  The
	formula is:

	   0*value0 + 1000*value1 + 2000*value2 + ...
	   --------------------------------------------
			 value0  +  value1  +  value2 + ...

	By default, this function assumes a dark line (high values)
	surrounded by white (low values).  If your line is light on
	black, set the optional second argument white_line to true.  In
	this case, each sensor value will be replaced by (1000-value)
	before the averaging.
	"""
	def LT_readLine(self, white_line = 0):

		sensor_values = self.LT_readCalibrated()
		avg = 0
		sum = 0
		on_line = 0
		for i in range(0,self.numSensors):
			value = sensor_values[i]
			if(white_line):
				value = 1000-value
			# keep track of whether we see the line at all
			if(value > 200):
				on_line = 1
				
			# only average in values that are above a noise threshold
			if(value > 50):
				avg += value * (i * 1000);  # this is for the weighted total,
				sum += value;                  #this is for the denominator 

		if(on_line != 1):
			# If it last read to the left of center, return 0.
			if(self.last_value < (self.numSensors - 1)*1000/2):
				#print("left")
				return 0;
	
			# If it last read to the right of center, return the max.
			else:
				#print("right")
				return (self.numSensors - 1)*1000

		self.last_value = avg/sum
		
		return self.last_value	
	
	###############################
	# METODES Infrared sensor Left - Right
	###############################	
	def getInfrared(self):
		DR_status = GPIO.input(self.DR)
		DL_status = GPIO.input(self.DL)
		return not bool(DL_status), not bool(DR_status)
	
	###############################
	# METODES Infrared sensor Left - Right
	###############################
	def forward(self):
		GPIO.output(self.IN1,GPIO.HIGH)
		GPIO.output(self.IN2,GPIO.LOW)
		GPIO.output(self.IN3,GPIO.LOW)
		GPIO.output(self.IN4,GPIO.HIGH)

	def stop(self):
		GPIO.output(self.IN1,GPIO.LOW)
		GPIO.output(self.IN2,GPIO.LOW)
		GPIO.output(self.IN3,GPIO.LOW)
		GPIO.output(self.IN4,GPIO.LOW)

	def backward(self):
		GPIO.output(self.IN1,GPIO.LOW)
		GPIO.output(self.IN2,GPIO.HIGH)
		GPIO.output(self.IN3,GPIO.HIGH)
		GPIO.output(self.IN4,GPIO.LOW)

	def left(self):
		GPIO.output(self.IN1,GPIO.LOW)
		GPIO.output(self.IN2,GPIO.LOW)
		GPIO.output(self.IN3,GPIO.LOW)
		GPIO.output(self.IN4,GPIO.HIGH)

	def right(self):
		GPIO.output(self.IN1,GPIO.HIGH)
		GPIO.output(self.IN2,GPIO.LOW)
		GPIO.output(self.IN3,GPIO.LOW)
		GPIO.output(self.IN4,GPIO.LOW)
		
	def setPWMA(self,value):
		self.PWMA.ChangeDutyCycle(value)

	def setPWMB(self,value):
		self.PWMB.ChangeDutyCycle(value)	
		
	def setMotor(self, left, right):
		#print "Set Motor" + left + right
		if(right == 0): #Stop
			self.counter_inc_r=0
			self.USD_disableInterupt_R()
			GPIO.output(self.IN1,GPIO.LOW)
			GPIO.output(self.IN2,GPIO.LOW)
		elif((right > 0) and (right <= 100)):
			self.counter_inc_r=1
			self.USD_enableInterupt_R()
			self.PWMA.ChangeDutyCycle(right)
			GPIO.output(self.IN1,GPIO.HIGH)
			GPIO.output(self.IN2,GPIO.LOW)
		elif((right < 0) and (right >= -100)):
			self.counter_inc_r=-1
			self.USD_enableInterupt_R()
			self.PWMA.ChangeDutyCycle(0 - right)
			GPIO.output(self.IN1,GPIO.LOW)
			GPIO.output(self.IN2,GPIO.HIGH)
			
		if (left==0):
			self.counter_inc_l=0
			self.USD_disableInterupt_L()
			GPIO.output(self.IN3,GPIO.LOW)
			GPIO.output(self.IN4,GPIO.LOW)
		elif((left > 0) and (left <= 100)):
			self.counter_inc_l=1
			self.USD_enableInterupt_L()
			self.PWMB.ChangeDutyCycle(left)
			GPIO.output(self.IN3,GPIO.LOW)
			GPIO.output(self.IN4,GPIO.HIGH)			
		elif((left < 0) and (left >= -100)):
			self.counter_inc_l=-1
			self.USD_enableInterupt_L()
			self.PWMB.ChangeDutyCycle(0 - left)
			GPIO.output(self.IN3,GPIO.HIGH)
			GPIO.output(self.IN4,GPIO.LOW)
			
			

	
