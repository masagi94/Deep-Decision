import cv2
import numpy as np
import socket
import torch
import torchvision
import threading
import queue
import pathlib


def receive_frame():
    
    while True:

        # Receive a UDP packet containing a JPEG image
        print("Listening on port ", port)
        data, addr = sock.recvfrom(65535)
        print("FRAME RECEIVED")
        frames_queue.put((data, addr))



def send_predictions():
    
    while True:
        while not frames_queue.empty():
            data, addr =  frames_queue.get()
            
            # process frame
            img_encoded = np.frombuffer(data, dtype=np.uint8)

            # Decode the JPEG image
            img = cv2.imdecode(img_encoded, cv2.IMREAD_COLOR)

            # predict on the image, and get results
#             results = np.array(model(img).pandas().xyxy[0])
            
            # new attempt
            results = model(img)
            r_img = results.render() # returns a list with the images as np.array
            img_with_boxes = r_img[0]
            # new attempt
            
            
            _, new_img_encoded = cv2.imencode('.jpg', img_with_boxes[:,:,::-1], encode_params)
            
            data = np.array(new_img_encoded)
            string_data = data.tobytes()
            try:
                sock.sendto(string_data, addr)
                print("FRAME SENT")
            except:
                print("******************************* ERROR - FRAME NOT SENT *******************************")



model = torch.hub.load('Ultralytics/yolov5', 'yolov5x')
model.conf = 0.70
model.cuda()
encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

frames_queue = queue.Queue()

ip = '192.168.1.189'
port = 5005

# Create a UDP socket and bind it to the specified IP address and port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))

t1 = threading.Thread(target=receive_frame)
t2 = threading.Thread(target=send_predictions)

t1.start()
t2.start()