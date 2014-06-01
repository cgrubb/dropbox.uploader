#!/usr/bin/python

import os
LOCAL_PATH = os.path.dirname(os.path.realpath(__file__))
import json
import zmq
from zmq.eventloop import zmqstream,ioloop
ioloop.install()

import dropbox

class DropboxServer():

	def __init__(self):
		self.context = zmq.Context()
		self.sub = self.context.socket(zmq.SUB)
		self.sub.connect("tcp://localhost:8891")
		self.sub.setsockopt(zmq.SUBSCRIBE,"scan")
		self.pub = self.context.socket(zmq.PUB)
		self.pub.bind("tcp://*:8892")
		self.loop = ioloop.IOLoop.instance()
		self.stream = zmqstream.ZMQStream(self.sub)
		self.stream.on_recv(self.handle_msg)
		#Get the dropbox access token
		with open('{}/tokens.txt'.format(LOCAL_PATH),'r') as token_file:
			info = token_file.read()
			self.access_token = info.split(',')[0]

def handle_msg(self, message):
	try:
		client = dropbox.client.DropboxClient(self.access_token)
		msg = json.loads(message[1])
		print msg
		files = msg['files']
		msg['uploads'] = []
		for f in files:
			with open(f, 'rb') as upload:
				print 'uploading ' + f
				response = client.put_file('/scans/{}'.format(os.path.basename(f)),
				                   upload)
				msg["uploads"].append(response)
		self.pub.send_multipart(['dropbox',
		 json.dumps(msg)])
	except ValueError:
		print "Invalid JSON message"
	except Exception as ex:
		print "Error: {}".format(ex.message)

def main():
	gen = DropboxServer()
	ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
