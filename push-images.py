#!/usr/bin/python2

import sys
import cv2
import cv2.cv as cv
import numpy
import zmq


if len(sys.argv) != 3:
	print("Usage: "+sys.argv[0]+" tcp://10.8.0.1:2000 tcp://10.8.0.1:3000")
	sys.exit(1)

images_endpoint = sys.argv[1]
config_endpoint = sys.argv[2]

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

vc = cv2.VideoCapture(0)

vc.set(cv.CV_CAP_PROP_FRAME_WIDTH, frame_width)
vc.set(cv.CV_CAP_PROP_FRAME_HEIGHT, frame_height)


images_context = zmq_context.socket(zmq.PUB)
#send_context.setsockopt(zmq.SUBSCRIBE,'')

images_context.setsockopt(zmq.SNDBUF,5)
images_context.setsockopt(zmq.RCVBUF,5)
images_context.setsockopt(zmq.SNDHWM,2)

images_context.connect(images_endpoint)

config_context = zmq_context.socket(zmq.PULL)
config_context.connect(config_endpoint)


def print_debug(text):
	if print_debug:
		print(text)

def update_config_values():
	global jpeg_quality, resize_frame_width, resize_frame_height
	try:
		config = config_context.recv_json(zmq.NOBLOCK)
		print_debug("Config data :"+str(config))
		
		if config["type"] == "config":
			if config["name"] == "jpeg_quality":
				jpeg_quality = int(config["value"])
			if config["name"] == "frame_resolution":
				values = str(config["value"]).split("x")
				resize_frame_width = int(values[0])
				resize_frame_height = int(values[1])
	
	except zmq.error.Again:
		pass

def process_frame(frame):
	if resize_frame_width != frame_width or resize_frame_height != frame_height:
		frame = cv2.resize(frame, (resize_frame_width, resize_frame_height)) 
		print_debug("Resixing frame to {}x{}".format(resize_frame_width,resize_frame_height))

def add_text(frame):
	height, width, depth = frame.shape
	txt = "{}x{} {}% {}kB".format(width,height,jpeg_quality,int(len(numpy.array(frame).tostring())/1024))
	cv2.putText(frame,txt, (10,100), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)

def send_frame(frame):
	images_context.send(frame)

while True:
		
	rval, frame = vc.read()

	process_frame(frame)

	if add_debug_text:
		add_text(frame)

	send_frame(frame)

	update_config_values()






