import cv2
import numpy as np
import socket
import torch
import torchvision
import threading
import queue

torch.set_num_threads(20)

# Threaded method used to listen for incomming frames sent by the client
def receive_frame():
    print("\n**********************************************************")
    print("\nReady to receive frames, listening from Receiver Thread...\n")

    while (user_input != 'q'):
        # Receive a UDP packet containing a JPEG image
        # print("Listening on port ", port)
        data, addr = sock.recvfrom(65535)
        
        # print("FRAME RECEIVED")
        
        # add frame to queue for processing
        frames_queue.put((data, addr))

    
    print("\nExiting Receiver Thread...\n")
    return()


# Threaded method used for processing and sending frames with bounding boxes to client
def send_predictions():
    
    while True:
        
        # Processes a frame once the queue is no longer empty
        while (not frames_queue.empty()) and (user_input != 'q'):
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
                # print("FRAME SENT")
            except:
                print("******************************* ERROR - FRAME NOT SENT *******************************")

        if (user_input == 'q'):
            print("\nExiting Predictions Thread...\n")
            return()



# Create the queue that will hold frames as they come in
frames_queue = queue.Queue()

# Import YOLO Model
model = torch.hub.load('Ultralytics/yolov5', 'yolov5x')

# only send detections above .70 confidence
model.conf = 0.70

encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 70]

# IP address of pc where server is running
ip = '192.168.1.189'
port = 5005

# Create a UDP socket and bind it to the specified IP address and port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))

# Create worker threads
t1 = threading.Thread(target=receive_frame)
t2 = threading.Thread(target=send_predictions)

user_input = ""

# start threads
t1.start()
t2.start()

# check user input to exit program
while True:
    user_input = input("\nType 'q' to quit\n")
    if(user_input == 'q'):
        print("\n\n***********************")
        print("Shutting down Server...")
        
        # send message to receiver thread to unblock it
        sock.sendto(bytes("exit", 'utf-8'), (ip,port))
        t1.join()
        t2.join()
        print("\n\n***********************")
        print("Threads quit successfully")
        exit()
    else:
        print("non valid input")

