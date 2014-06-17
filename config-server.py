#!/usr/bin/python3

import zmq
import time
import sys

jpeg_quality = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100] 

resolution = ["640x480", "960x544", "1280x720"]

resolution = ["640x480"]

if len(sys.argv) != 2:
	print("Usage: "+sys.argv[0]+" tcp://0.0.0.0:3000")
	sys.exit(1)

connect_to_config = sys.argv[1]

context = zmq.Context()

config_context = context.socket(zmq.PUSH)
config_context.bind(connect_to_config)

def send_packet(packet):
	print(packet)
	config_context.send_json(packet)	

while True:
	for quality in jpeg_quality:
		packet = {"type":"config", "name":"jpeg_quality", "value":quality}
		send_packet(packet)
		
		for res in resolution:
			packet = {"type":"config", "name":"frame_resolution", "value":res}
			send_packet(packet)
			time.sleep(3)
		
