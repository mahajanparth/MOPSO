import cv2
import numpy as np
"""
class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			#self.file = open(filename, 'rb')
			self.cam=cv2.VideoCapture(-1)
			print("hello")
		except:
			raise IOError
		self.frameNum = 0
		
	def nextFrame(self):
		Get next frame.
		#data = self.file.read(5) # Get the framelength from the first 5 bits
		if self.cam.isOpened():

			#framelength = int(data)
							
			# Read the current frame
			#data = self.file.read(framelength)
			ret,data=self.cam.read()
			im_resize = cv2.resize(data, (200, 200))

			is_success, im_buf_arr = cv2.imencode(".jpg", im_resize)
			data= im_buf_arr.tobytes()

			self.frameNum += 1
		return data
		
	def frameNbr(self):
		Get frame number.
		return self.frameNum
"""


class VideoStream:
	def __init__(self, shared_array,img_shape):
		self.frameNum = 0
		self.shared_array=shared_array
		self.img_shape=img_shape
	def nextFrame(self):
		"""Get next frame."""
		#data = self.file.read(5) # Get the framelength from the first 5 bits
		data=np.frombuffer(self.shared_array, dtype=np.float64).reshape(self.img_shape)
		data=data.astype("uint8")

		im_resize = cv2.resize(data, (640, 480))
		encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 40]
		is_success, im_buf_arr = cv2.imencode('.jpg', im_resize, encode_param)
		# is_success, im_buf_arr = cv2.imencode(".jpeg", im_resize)
		data = im_buf_arr.tobytes()

		self.frameNum += 1
		return data
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum
	
	