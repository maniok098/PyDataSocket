# PyDataSocket
This module provides the implementation of sending raw data in Python and receiving raw data in Matlab. The bytes-like socket objects are directly transmitted from Python to Matlab without any processing. Meanwhile, the encoding/decoding process for the original data is accomplished by user-defined function in "main.py"/"main.m".

## Install
This module has not been packaged, and there is no need to install.

## Basic procedure
1) open "main.m" in Matlab, check the ip and port
2) run "main.m" to start receiving data in Matlab
3) open "main.py" in Python, check the ip and port and edit "send_sig()" if necessary
4) run "main.py" to start sending data in Python
5) enjoy your data

## SendSocket() in Python
The bytes-like socket object is directly sent to Matlab without processing. The original data should be preprocessed and converted to bytes-like object by user-defined function in "main.py".

## ReceiveSocket() in Matlab
The bytes-like socket object is directly received from Python without processing. The callback function will be called everytime a new chunk of data is recieved. And the callback function is defined by users in "main.m" in order to process the RAW data.

## Dataflow
original data --> json --> bytes --> server --> client --> bytes --> json --> original data 
