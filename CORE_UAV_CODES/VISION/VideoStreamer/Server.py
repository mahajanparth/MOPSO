import sys, socket

from VideoStreamer.ServerWorker import ServerWorker

class Server:	
	
	def main(self,event,shared_img,img_shape,sysid=0):
		try:
			SERVER_PORT = int(sys.argv[1])

		except:
			#print ("[Usage: Server.py Server_port]\n")
			SERVER_PORT = 7000+int(sysid)
		print("STARTED SERVER",SERVER_PORT)
		rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		rtspSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		rtspSocket.bind(('', SERVER_PORT))
		rtspSocket.listen(5)        

		# Receive client info (address,port) through RTSP/TCP session
		while True:
			print("STARTING_SERVER")
			clientInfo = {}
			clientInfo['rtspSocket'] = rtspSocket.accept()
			ServerWorker(clientInfo,shared_img,img_shape).run()

if __name__ == "__main__":
	(Server()).main()


