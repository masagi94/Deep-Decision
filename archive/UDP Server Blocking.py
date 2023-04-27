import cv2
import numpy as np
import socket
import torch
import torchvision

# Model
model = torch.hub.load('Ultralytics/yolov5', 'yolov5x')
model.cuda()
# Images
for f in 'zidane.jpg', 'bus.jpg':
    torch.hub.download_url_to_file('https://ultralytics.com/images/' + f, f)  # download 2 images
# im1 = Image.open('zidane.jpg')  # PIL image
im2 = cv2.imread('bus.jpg')[..., ::-1]  # OpenCV image (BGR to RGB)


# Define the IP address and port number to receive UDP packets from
ip = '192.168.1.189'
port = 5005

# Create a UDP socket and bind it to the specified IP address and port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))

# Define the window name
window_name = "Video Stream"

# Loop until the user presses the 'q' key or the window is closed
while True:
    # Receive a UDP packet containing a JPEG image
    print("listening...")
    data, addr = sock.recvfrom(65535)
    print("RECEIVED...")
    img_encoded = np.frombuffer(data, dtype=np.uint8)

    # Decode the JPEG image
    img = cv2.imdecode(img_encoded, cv2.IMREAD_COLOR)

    # predict on the image, and get results
    results = np.array(model(img).pandas().xyxy[0].iloc[0])
    print("DETECTED:", results[6])
    encoded_results = np.char.encode(np.array2string(results, precision=2, separator=',',suppress_small=True))
#     encoded_bytes = encoded_results.tobytes()
    # send back the results
    sock.sendto(encoded_results, addr)
    print("RESPONSE SENT")
    
    # Display the image in a window
#     cv2.imshow(window_name, img)

    # Wait for 1 millisecond, and check if the user pressed the 'q' key or the window was closed
#     key = cv2.waitKey(1) & 0xFF
#     if key == ord('q') or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
#         break

# Close the window and release the UDP socket
cv2.destroyAllWindows()
sock.close()