from __future__ import print_function
import os
import threading
import serial  # module for serial port communication
import signal
import socket
import sys
import termios
import time
import tty
from picamera import PiCamera, Color
from time import sleep
from tensorflow.python.keras.models import load_model
import tensorflow as tf
from time import time
import numpy as np
from PIL import Image

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
MODEL_NAME = '/home/pi/Desktop/inceptionv3_light.hd5'
start=time()
model = load_model(MODEL_NAME)
end = time()
print("load model time : {}".format(end-start))
dict = {0: 'Maine Coon cat', 1: 'Ocelot cat', 2: 'Singapura cat', 3: 'Turkish Van cat'}
graph = tf.get_default_graph()

catmessage = ""

def classify():
    global catmessage
    global model
    catmessage = "Proccessing"
    image = load_image('/home/pi/Desktop/test.jpg')
    global graph
    with graph.as_default():
        result = model.predict(image)
        themax = np.argmax(result)
    catmessage = ("%3.2f %s."%( result[0][themax],dict[themax]))
    return (dict[themax], result[0][themax], themax)


# In[6]:


def load_image(image_fname):
    img = Image.open(image_fname)
    img = img.resize((299, 299))
    imgarray = np.array(img)/255.0
    final = np.expand_dims(imgarray, axis = 0)
    return final

# global flag
# flag = True

def emergency( signal, frame):
    print('Something went wrong!')
    sys.exit(0)


def shakehand():
    ser.write('hello\n'.encode('utf-8'))
    res = ser.readline()
    print(res.decode('utf-8'))
    if res.decode('utf-8') == 'ack\n':
        print("ardino online")
        ser.write('ack\n'.encode('utf-8'))
        global flag
        flag = False
        print("succeed")
        # ser.close()


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def run(camera):
    signal.signal(signal.SIGINT, emergency)
    HOST_IP = get_host_ip()  # 我的树莓派作为AP热点的ip地址
    HOST_PORT = 7654  # 端口号
    print("Starting socket: TCP...")
    socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("TCP server listen @ %s:%d!" % (HOST_IP, HOST_PORT))
    host_addr = (HOST_IP, HOST_PORT)
    # TCPServer.allow_reuse_address = True
    socket_tcp.bind(host_addr)  
    socket_tcp.listen(1)

    while True:
        print('waiting for connection...')
        socket_con, (client_ip, client_port) = socket_tcp.accept()  # 接收客户端的请求
        print("Connection accepted from %s. timeout=10" % client_ip)
        socket_con.settimeout(20)
        while True:
            try:
                data = socket_con.recv(512)  # 接收数据
                # print(data)
            except socket.timeout:
                print("timeout")
                socket_con.close()
                break
            except ConnectionResetError:
                print("connectionResetError")
                socket_con.close()
                break

            if data:                  # print(data.decode('utf-8'))
                data = data.decode('utf-8')
                data1 = data.split('\n')
                # print(1)
                for sdata in data1:
                    #print(sdata)
                    if sdata == "photo":
                        print("photo")
                        ser.write('!'.encode('utf-8'))
                        ser.write('!'.encode('utf-8'))
                        ser.write('!'.encode('utf-8'))
                        ser.write('!'.encode('utf-8'))
                        camera.capture('/home/pi/Desktop/test.jpg')
                        classify()
                        #catreg = threading.Thread(target=classify)
        # server_thread.daemon = True
                        #catreg.start()
                        #label, prob, _ = classify(model, img)
                        
                    elif sdata == "stop":
                        ser.write('!'.encode('utf-8'))
                        ser.write('!'.encode('utf-8'))
                        ser.write('!'.encode('utf-8'))
                        ser.write('!'.encode('utf-8'))
                        print('stop')

                    elif "," in sdata:
                        try:
                            lspeed = int(sdata.split(',')[0])
                            rspeed = int(sdata.split(',')[1])
                        except:
                            break
                            pass
                        if lspeed <= 0 and rspeed <= 0:
                            sig = '1'
                        elif lspeed < 0 and rspeed > 0:
                            sig = '2'
                        elif lspeed > 0 and rspeed < 0:
                            sig = '3'
                        else:
                            sig = '4'

                        # print(str(sig) + " " + str(lspeed) + " " + str(rspeed))

                        if lspeed < 0: lspeed *= -1
                        if rspeed < 0: rspeed *= -1
                        if lspeed > 255: lspeed = 255
                        if rspeed > 255: rspeed = 255

                        if lspeed == 35 or lspeed == 33:
                            lspeed = 36
                        if rspeed == 35 or lspeed == 33:
                            rspeed = 36
                        lspeed = lspeed.to_bytes(1, byteorder='big')
                        rspeed = rspeed.to_bytes(1, byteorder='big')
                        sig = sig.encode('utf-8')
                        ser.write('#'.encode('utf-8'))
                        ser.write(lspeed)
                        ser.write(rspeed)
                        ser.write(sig)
                        
                    response = ser.read_all().decode('utf-8')
                    distance = response.split("\n")
                    data_dis = distance[len(distance)-2]
                    if ',' in data_dis:
                        print(': {}'.format(data_dis))
                        data_dis += ','
                        data_dis += catmessage
                        data_dis += '\n'
                        try:
                            socket_con.send(data_dis.encode('utf-8'))
                        except BrokenPipeError:
                            print("Connect broken pipe")
                            break
            else:
                print("disconnnected")
                socket_con.close()
                break
