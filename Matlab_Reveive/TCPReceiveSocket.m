classdef TCPReceiveSocket < handle
% The bytes-like object is directly received from Python without any processing.
% The decoding functional should be implemented by users, i.e. in
% callback_function.
    properties
      callback
      ip
      port
      socket
   end
   methods
      function obj = TCPReceiveSocket(tcp_port, tcp_ip, callback_function)
         if nargin == 3
            obj.ip = tcp_ip;
            obj.port = tcp_port;
            obj.callback = callback_function;
            obj.socket = tcpip(tcp_ip, tcp_port, 'NetworkRole', 'client');
            % InputBufferSize = 512 by default. Increase this parameter for
            % large messages.
            obj.socket.InputBufferSize = 300000;     
            obj.socket.ByteOrder = 'littleEndian';
            set(obj.socket,'BytesAvailableFcn', @obj.callback_wrapper);
            set(obj.socket,'ReadAsyncMode', 'continuous');
            set(obj.socket, 'TransferDelay', 'off');
            obj.socket.BytesAvailableFcnMode = 'byte';
            obj.socket.BytesAvailableFcnCount = 4;
         else
            error('Need to supply tcp_port, tcp_ip, and a callback_function')
         end
      end
      
      function start(self)
          is_started = false;
          while ~is_started
              try
                  fopen(self.socket);
              catch
                  continue
              end
              is_started = true;
          end
      end
      
      function stop(self)
        fclose(self.socket);
      end
      
      function callback_wrapper(self, socket, ~)
          % return if for some reason this function got called and there
          % isn't enough data.
          if socket.BytesAvailable < 4
            return
          end         
          % read in the length of the message
          length = fread(socket, 1, 'int32');
            while socket.BytesAvailable < length
                % wait till the entire message is there. Should possibly
                % add a wait here to not tax the CPU, but realistically,
                % the data is likely already there.
            end
            % pass the socket object to user-defined callback function without processing
            data_raw = socket;         
            self.callback(data_raw,length)
          end
      end
end