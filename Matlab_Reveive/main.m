% Receive directly the bytes-like socket object (RAW Data) from Python
% and process it in user-defined callback function. 
clear all
close all 
clc

rec_socket = TCPReceiveSocket(9658,'127.0.0.1',   @echo_back);
% use '127.0.0.1' for windows and 'localhost' for unix systems

'start receive'
rec_socket.start()

pause(50) % arbitrarily stay open for 50 seconds to receive the messages
          % from python, an input method can be used to interrupt the receiving process
rec_socket.stop();

function echo_back(data_raw,length)
% user defined callback function
% data_raw: the received bytes-like obejct, i.e. socket object
% length: the length of the message
data = jsondecode(fscanf(data_raw, '%c', double(length)))
end