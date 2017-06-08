from flask import Flask, request
from flask_restful import Resource, Api
from flask_restful import reqparse
from AlphaBot import AlphaBot

import sys
#import pyhsm

debug = True

app = Flask(__name__)
api = Api(app)

#to awoid CORS problems
@app.after_request 
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

Ab = AlphaBot()
  
##
##  CLASS RESTlet
##
class AlphaBot_Motor(Resource):
	def post(self):
		print "POST_ENCODING"
				
		parser = reqparse.RequestParser()
		parser.add_argument('left' , required=True, type=int, help='Left speed motor missing!!!')
		parser.add_argument('right', required=True, type=int, help='Right speed motor missing!!!')
		args = parser.parse_args()
               
		left = args['left']
		right = args['right']
		
		if(left > 100):
			left=100
		elif (left < -100):
			left= -100
		if(right > 100):
			right=100
		elif (right < -100):
			right= -100
		print "Left motor speed::" + str(left)
		print "Right motor speed::" + str(right)
		
		Ab.setMotor(left,right)
		
		return {"ret": "OK"}

class AlphaBot_InfraRed(Resource):
	def post(self):
		dl,dr = Ab.getInfrared()
		return {"ret": "OK", "left":dl, "right":dr}

class AlphaBot_lt_calibrate(Resource):
	def post(self):
		print "Start Calibrate"
		for i in range(0,50):
			Ab.LT_calibrate()
		print "Finish Calibrate"
		return {"ret": "OK"}
		
class AlphaBot_lt_read(Resource):
	def post(self):
		ret_val = Ab.LT_readLine()
		return {"ret": "OK", "value":ret_val}

class AlphaBot_motorcount(Resource):
	def post(self):
		cleft,cright  = Ab.USD_GetSpeedCounter()
		return {"ret": "OK", "left":cleft, "right":cright}
		
		
api.add_resource(AlphaBot_Motor, '/AlphaBot/motor')
api.add_resource(AlphaBot_InfraRed, '/AlphaBot/infrared')
api.add_resource(AlphaBot_lt_calibrate, '/AlphaBot/lt_calibrate')
api.add_resource(AlphaBot_lt_read, '/AlphaBot/lt_read')
api.add_resource(AlphaBot_motorcount, '/AlphaBot/motorcount')



if __name__ == '__main__':
	Ab.stop()
	app.run(host="192.168.2.141",port=9999, debug=debug)
	
	
