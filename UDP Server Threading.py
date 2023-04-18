import cv2
import numpy as np
import socket
import torch
import torchvision
import threading
import queue
import pathlib


# Threaded method used to listen for incomming frames sent by the client
def receive_frame():
    
    while True:
        # Receive a UDP packet containing a JPEG image
        print("Listening on port ", port)
        data, addr = sock.recvfrom(65535)
        
        print("FRAME RECEIVED")
        
        # add frame to queue for processing
        frames_queue.put((data, addr))



# Threaded method used for processing and sending frames with bounding boxes to client
def send_predictions():
    
    while True:
        
        # Processes a frame once the queue is no longer empty
        while not frames_queue.empty():
            data, addr =  frames_queue.get()
            
            # read frame
            img_encoded = np.frombuffer(data, dtype=np.uint8)

            # Decode the JPEG frame
            img = cv2.imdecode(img_encoded, cv2.IMREAD_COLOR)
            
            # Get predictions on frame from model
            results = model(img)
            
            # Render the predicted bounding boxes on the frame
            r_img = results.render()
            img_with_boxes = r_img[0]
            
            # Encode frame to send to client
            _, new_img_encoded = cv2.imencode('.jpg', img_with_boxes[:,:,::-1], encode_params)
            data = np.array(new_img_encoded)
            string_data = data.tobytes()
            
            # Try to send frame to client
            # Sometimes fails if frame size is too big
            try:
                sock.sendto(string_data, addr)
                print("FRAME SENT")
            except:
                print("******************************* ERROR - FRAME NOT SENT *******************************")



# Create the queue that will hold frames as they come in
frames_queue = queue.Queue()

# Import YOLO Model
model = torch.hub.load('Ultralytics/yolov5', 'yolov5s')

# only send detections above .70 confidence
model.conf = 0.70

encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

# IP address of pc where server is running
ip = '192.168.1.189'
port = 5005

# Create a UDP socket and bind it to the specified IP address and port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))

# Create worker threads
t1 = threading.Thread(target=receive_frame)
t2 = threading.Thread(target=send_predictions)

# start threads
t1.start()
t2.start()