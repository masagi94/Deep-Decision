# Purpose
Purpose of the project is to replicate the DeepDecision framework by
1. Creating a backend implementation that accepts images through a socket
2. Create a frontend implementation to work on laptop only

# How to Install
Requires Python 3.9 and Anaconda (or any Conda). Then, you'll need to create a virtual environment via conda using the requirements.txt file we have like so:
```pip install -r requirements.txt```

If you have an NVIDIA GPU, and you wish to utilize it, then you will need to install CUDA both onto your PC and with pip.
[CUDA Quick Guide](https://docs.nvidia.com/cuda/cuda-quick-start-guide/index.html)

# How to Run
1. Make sure to set the IP address in the Server files to whatever one your current device is set to.
2. Make sure to set the IP address in the client file to whatever is the device's running that. 
3. Run the backend first, either the jupyter notebook (run on CPU) or python file (run on GPU)
4. Then run the Client file on another device within the same network
5. Feel free to adjust the latency and which client device is offloading by typing it into the console
        - 
        - 

# Files
There are 3 versions of UDP Server, which are designed for running on a server:
- UDP Server Blocking.py - Old version of server, no longer using, archived
- UDP Server Threading.py - New version of server, most up to date
- UDP Server Threading.ipynb - Same as the .py one, but Jupyter Notebook is easier to visualize results with

UDP Client is for a laptop device.

## Note
To run the server with yolov5x on an NVIDIA GPU, use the "UDP Server Threading.py" file instead of the Jupyter Notebook one. Jupyter Notebook will NOT work with the GPU, not sure why.

# Features

## Backend
- Able to accept images sent through a socket for any mobile device (Android and Laptop)
    - User can input in the console which mobile device is sending data
- User can input a number to indicate the latency value in milliseconds (ms)
- Runs a YOLOv5x on GPU (if using the python file, not the notebook) for object detection
- Returns a new image with bounding boxes displayed

## Frontend
- Perform on-device processing via YOLOv5s on CPU
- Display camera and bounding boxes along with FPS and latency
- Send images via a socket to a backend for processing
- Produce basic decisions on processing locally or offloading by:
    - Battery percent and status
    - FPS and Latency