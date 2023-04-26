import cv2
import numpy as np
import socket
import time
import torch
import torchvision
import threading
from multiprocessing import Manager

# torch.set_num_threads(20)

# Threaded method used to listen for incomming UDP frames sent by the client.
# Add received JPEG images to queue for processing.
def receive_frame():
    print("\n**********************************************************")
    print("\nReady to receive frames...\n")
    print("\nListening on:",(ip, port),"\n")

    while (user_input != 'q'):
        data, addr = sock.recvfrom(65535)
        frames_process_queue.put((data, addr))

    print("\nExiting Receiver Thread...\n")
    return()


# Threaded method used for processing frames and drawing bounding boxes. Adds them
# to sending queue
def process_frame():
    while True:
        
        # Processes a frame once the queue is no longer empty
        while (not frames_process_queue.empty()) and (user_input != 'q'):
            # get frame and decode
            
            data, addr =  frames_process_queue.get()
            img_encoded = np.frombuffer(data, dtype=np.uint8) 
            img = cv2.imdecode(img_encoded, cv2.IMREAD_COLOR)
            
            # invert image if we're using phone or laptop as client
            if(invert_image):
                img = img[:,:,::-1]

            # Get predictions on frame from model
            results = model(img)
            
            # Render the predicted bounding boxes on the frame
            r_img = results.render()
            img_with_boxes = r_img[0]

            # Encode frame to send to client
            _, new_img_encoded = cv2.imencode('.jpg', img_with_boxes[:,:,::-1], encode_params)
            data = np.array(new_img_encoded)
            string_data = data.tobytes()
            
            predictions_send_queue.put((string_data, addr))

        if (user_input == 'q'):
            print("\nExiting Processing Thread...\n")
            return()

# Threaded method for sending predictions back to client.
# Pops predictions from the send queue.
def send_predictions():
    while True:
        while((not predictions_send_queue.empty()) and (user_input != 'q')):
            
            # pop prediction and send it
            data, addr =  predictions_send_queue.get()
            
            try:
                sock.sendto(data, addr)
            except:
                print("******************************* ERROR - FRAME NOT SENT *******************************")

            # delay packets, latency specified by user
            time.sleep(send_latency/1000)
            
            # clear queue, otherwise the delay stacks
            try:
                while True:
                    predictions_send_queue.get_nowait()
            except:
                pass
        
        if (user_input == 'q'):
            print("\nExiting Sending Thread...\n")
            return()

if __name__ == '__main__':
    manager1 = Manager()

    # Create the queue that will hold frames as they come in
    frames_process_queue = manager1.Queue()
    predictions_send_queue = manager1.Queue()

    # Import YOLO Model
    model = torch.hub.load('Ultralytics/yolov5', 'yolov5x', trust_repo=True, force_reload=True).to("cuda")
    model.conf = 0.70

    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 70]

    # Create a UDP socket and bind it to the specified IP address and port of the server
    ip = '192.168.1.189'
    port = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))

    # Create worker threads
    t1 = threading.Thread(target=receive_frame)
    t2 = threading.Thread(target=process_frame)
    t3 = threading.Thread(target=send_predictions)
    user_input = ""
    send_latency = 0
    invert_image = False
    t1.start()
    t2.start()
    t3.start()

    # check user input to update server functionality, or exit program
    while True:
        user_input = input("\n\n\n--User options--\n" + 
                            "   Type:\n"+
                            "       'q'          -- shuts down the server\n"+
                            "       int (0-1000) -- adds latency (ms)\n" +
                            "       'phone'      -- sets client as phone\n"+
                            "       'laptop'     -- sets client as laptop\n\n"+
                            "   Input: ")


        if(user_input == 'q'):
            print("\n\n***********************")
            print("Shutting down Server...")
            
            # send message to receiver thread to unblock it
            sock.sendto(bytes("exit", 'utf-8'), (ip,port))
            t1.join()
            t2.join()
            t3.join()
            print("\n\n***********************")
            print("Threads quit successfully")
            exit()

        elif(user_input == 'phone'):
            print("\nPhone Client Selected")
            invert_image = True

        elif(user_input == 'laptop'):
            print("\nLaptop Client Selected")
            invert_image = False

        elif(user_input.isdigit()):
            send_latency = int(user_input)
            print("\nLatency updated to: " + str(user_input) + " ms\n")

        else:
            print("\n*** INVALID INPUT ***\n")
