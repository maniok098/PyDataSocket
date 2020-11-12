from threading import Event, Thread
from socket import socket, AF_INET, SOCK_STREAM, IPPROTO_TCP, TCP_NODELAY, SOL_SOCKET, SO_REUSEADDR
import time
import struct

def _get_socket():
    new_socket = socket(AF_INET, SOCK_STREAM)
    new_socket.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
    new_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    return new_socket


class TCPSendSocket(object):
    def __init__(self, tcp_port, tcp_ip='localhost', verbose=True, as_server=True, include_time=False):
        """
        A TCP socket class to send data to a specific port and address.
        :param tcp_port: TCP port to use.
        :param tcp_ip: ip address to connect to.
        :param verbose: Whether or not to print errors and status messages.
        :param as_server: Whether to run this socket as a server (default: True) or client. When run as a server, the
               socket supports multiple clients and sends each message to every connected client.
        :param include_time: Appends time.time() value when sending the data message.
        """
        self.data_to_send = b'0'
        self.data_size = 0
        self.port = int(tcp_port)
        self.ip = tcp_ip
        self.new_value_available = Event()
        self.stop_thread = Event()
        self.socket = _get_socket()
        self.verbose = verbose
        self.as_server = as_server
        self.include_time = include_time
        self.connected_clients = []
        self._gather_connections_thread = Thread(target=self._gather_connections)
        self.sending_thread = Thread(target=self._run)

    def send_data(self, data, data_size):
        """
        Send the RAW data to the socket.
        :param data: the format of data is RAW data.
        :param data_size: length of the data.
        :return: Nothing
        """
        self.data_to_send = data
        self.data_size = data_size
        self.new_value_available.set()

    def start(self, blocking=False):
        """
        Start the socket service.
        :param blocking: Will block the calling thread until a connection is established to at least one receiver.
        :return: Nothing
        """
        self._establish_connection()
        self.sending_thread.start()
        if blocking:
            while not len(self.connected_clients) > 0:
                time.sleep(0.05)

    def stop(self):
        """
        Stop the socket and it's associated threads.
        """
        self.stop_thread.set()
        if self._gather_connections_thread.is_alive():
            self._gather_connections_thread.join(timeout=2)
        if self.sending_thread.is_alive():
            self.sending_thread.join(timeout=2)
        self.socket.close()

    def _gather_connections(self):
        self.socket.bind((self.ip, self.port))
        self.socket.setblocking(0)
        if self.verbose:
            print('listening on port ', self.port)
        self.socket.listen(1)

        while not self.stop_thread.is_set():
            clients_to_remove = []
            for client in self.connected_clients:
                if not client[2]:
                    clients_to_remove.append(client)
            for client in clients_to_remove:
                self.connected_clients.remove(client)

            if self.stop_thread.is_set():
                return
            try:
                connection, client_address = self.socket.accept()
            except BlockingIOError:
                continue
            new_connection = [connection, client_address, True]
            self.connected_clients.append(new_connection)  # boolean is for connected

    def _establish_connection(self):
        while not len(self.connected_clients) > 0:
            if self.stop_thread.is_set():
                break
            if self.as_server and not self._gather_connections_thread.is_alive():
                self._gather_connections_thread.start()
                break
            else:
                while not len(self.connected_clients) > 0:
                    try:
                        self.socket.connect((self.ip, self.port))
                    except (ConnectionError, OSError) as e:
                        self.socket = _get_socket()
                        time.sleep(0.001)
                        continue
                    self.connected_clients.append([self.socket, 0, True])

    def _run(self):
        while not self.stop_thread.is_set():
            while not self.new_value_available.is_set():
                time.sleep(0.0001)
                if self.stop_thread.is_set():
                    return
            if self.stop_thread.is_set():
                return
            self._send_data()
            self.new_value_available.clear()

    def _send_data(self):
        if len(self.connected_clients) < 1:
            return
        data_raw = self.data_to_send  # RAW data
        size = self.data_size  # length of the data
        [self._send_f(connection, size, data_raw) for connection in self.connected_clients]

    def _send_f(self, connection, size, file):
        try:
            connection[0].send(struct.pack('I', size))  # Send the length of the data
            connection[0].sendall(file)  # Send RAW data
        except ConnectionError as e:
            if self.verbose:
                print(e)
            connection[2] = False
