#!/usr/bin/python2

import sys
import cv2
import cv2.cv as cv
import numpy
import zmq
import time


if len(sys.argv) != 4:
	print("Usage: "+sys.argv[0]+" tcp://10.8.0.1:2000 tcp://10.8.0.1:3000 tcp://10.8.0.1:4000")
	sys.exit(1)

images_endpoint = sys.argv[1]
config_endpoint = sys.argv[2]
bridge_endpoint = sys.argv[3]

zmq_context = zmq.Context()


frame_width = 1280
frame_height = 720

print_debug = True
add_debug_text = True

# Default values
resize_frame_width = 1280
resize_frame_height = 720

jpeg_quality = 10
current_fps= 0

metric_period = 1
# 5 seconds
last_metric_exec = time.time()

frame_count = 0

vc = cv2.VideoCapture(0)

vc.set(cv.CV_CAP_PROP_FRAME_WIDTH, frame_width)
vc.set(cv.CV_CAP_PROP_FRAME_HEIGHT, frame_height)


# Create images endpoint
images_context = zmq_context.socket(zmq.PUB)
#send_context.setsockopt(zmq.SUBSCRIBE,'')

images_context.setsockopt(zmq.SNDBUF,50000)
images_context.setsockopt(zmq.RCVBUF,50000)
images_context.setsockopt(zmq.SNDHWM,20)

images_context.connect(images_endpoint)


# Create configuration endpoint
config_context = zmq_context.socket(zmq.PULL)
config_context.connect(config_endpoint)


# Create metrics endpoint
metrics_context = zmq_context.socket(zmq.PUSH)
metrics_context.connect(bridge_endpoint)


encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),jpeg_quality]


def print_debug(text):
	if print_debug:
		print(text)

def update_config_values():
	global jpeg_quality, resize_frame_width, resize_frame_height, encode_param
	try:
		config = config_context.recv_json(zmq.NOBLOCK)
		print_debug("Config data :"+str(config))
		
		if config["type"] == "config":
			if config["name"] == "jpeg_quality":
				jpeg_quality = int(config["value"])
				encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),jpeg_quality]
			if config["name"] == "frame_resolution":
				values = str(config["value"]).split("x")
				resize_frame_width = int(values[0])
				resize_frame_height = int(values[1])
	
	except zmq.error.Again:
		pass

def process_frame():
	global frame
	if resize_frame_width != frame_width or resize_frame_height != frame_height:
		frame = cv2.resize(frame, (resize_frame_width, resize_frame_height)) 
		print_debug("Resizing frame to {}x{}".format(resize_frame_width,resize_frame_height))

def add_text():
	global frame
	height, width, depth = frame.shape
	txt = "{}x{} {}%".format(width,height,jpeg_quality)
	cv2.putText(frame,txt, (10,100), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)

def send_frame():
	global frame,frame_count
	ret, jpg = cv2.imencode( '.jpg', frame,encode_param)
	images_context.send(jpg.tostring())
	frame_count += 1

def process_merics():
	global last_metric_exec, frame_count

	if time.time() >= (last_metric_exec + metric_period):
		print("Sending metrics : ")

		fps = frame_count / metric_period
		print_debug("FPS : "+str(fps))

		packet = {"type":"metrics-push","name":"fps","value":fps}
		print_debug(packet)

		metrics_context.send_json(packet)


		frame_count = 0
		last_metric_exec = time.time()


while True:
		
	rval, frame = vc.read()

	process_frame()

	if add_debug_text:
		#pass
		add_text()

	send_frame()

	update_config_values()

	process_merics()

	

	





