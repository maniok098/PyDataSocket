from TestSocket import TCPSendSocket
import time
import numpy as np
import threading
import sys
import json

send_port = 9658
ip = '127.0.0.1'

# create a send socket
send_socket = TCPSendSocket(tcp_port=send_port, tcp_ip=ip)
# start the socket
send_socket.start()
stop_flag = threading.Event()

def send_sig():
# pass the bytes-like object and the length of the data to socket
    while not stop_flag.is_set():
      data = np.random.random((100,100)).tolist()
      data_as_bytes =json.dumps(data).encode()      # data are converted to bytes-like object
      size = len(data_as_bytes)                     # length of the data
      send_socket.send_data(data_as_bytes,size)
      time.sleep(2)

thread = threading.Thread(target=send_sig)
thread.start()

input('Press enter to shutdown.')
stop_flag.set()
thread.join()

# close the sockets
send_socket.stop()
sys.exit(0)