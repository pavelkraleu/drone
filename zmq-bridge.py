#!/usr/bin/python3

import sys
import zmq

if len(sys.argv) != 4:
	print("Usage: "+sys.argv[0]+" bridge_type listen_endpoint connect_to")
	print("")
	print("brige_type : {telemetry,images,config}")
	print("listen_endpoint : ZMQ listening endpoint - tcp://0.0.0.0:4000")
	print("connect_to : ZMQ listening endpoint for WS server - tcp://0.0.0.0:5000")
	sys.exit(1)

bridge_type = sys.argv[1]
listen_endpoint = sys.argv[2]
ws_endpoint = sys.argv[3]

allowed_types = ("telemetry","images","config")

if bridge_type not in allowed_types:
	print("bridge_type '"+bridge_type+"' is not allowed")



zmq_context = zmq.Context()

if bridge_type == "telemetry":
	listen_context = zmq_context.socket(zmq.PULL)
else:
	listen_context = zmq_context.socket(zmq.SUB)

listen_context.bind(listen_endpoint)


while True:
	packet = listen_context.recv_json()

	print(packet)

