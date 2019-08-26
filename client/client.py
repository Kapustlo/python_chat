import socket
import threading
import time
import json

class Client:
    def __init__(self, username, address, server, config):
        self.username = username

        self.address = address
        self.server = server

        self.config = config

        self.shutdown = True
        self.joined = False
        self.connected = False
        self.failed = False

        self.CHARSET = config.get("charset") if config.get("charset") else "utf-8"

        self.timeout = 5

        self.last_sent = None
        self.last_received = time.time()

    def _get_response_text(self, data):
        username = data["from"]
        text = data["text"]

        return "[{}]: {}".format(username, text)

    def _parse_response_data(self, data):
        return json.loads(data.decode(self.CHARSET))

    def __receiver(self, sock):
        print("Trying to connect to the server...")
        while not self.shutdown:
            while True:
                last_sent = self.last_sent if self.last_sent else time.time()
                if (time.time() - self.start_time >= self.timeout and not self.connected) or time.time() - self.last_received >= self.timeout:
                    self.stop()
                    self.failed = True
                    print("Failed to connect to the server, press 'Enter' to continue")
                    break
                try:
                    data, address = sock.recvfrom(self.config["buf_size"])
                    if not self.connected:
                        self.connected = True
                        print("Success")

                    self.last_sent = None

                    if data != b'1':
                        print(self._get_response_text(self._parse_response_data(data)))
                    else:
                        self.last_received = time.time()

                except Exception as e:
                    break

    def stop(self):
        self.shutdown = True
        self.joined = False

        print("Disconnected")

    def __login(self, username):
        self.joined = True

        self.socket_server.sendto(
            json.dumps({
                "type": "join",
                "username": self.username,
                "from": self.username
            }).encode(self.CHARSET),
            self.server
        )

    def run(self):
        try:
            self.start_time = time.time()

            print("Opening a socket...")
            self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_server.bind(self.address)
            self.socket_server.setblocking(0)
            socket_address = self.socket_server.getsockname()
            print("Opened socket on {}:{}".format(socket_address[0], socket_address[1]))

            self.shutdown = False

            self.__main_thread__ = threading.Thread(target=self.__receiver, args=(self.socket_server,))
            self.__main_thread__.start()

            self.__login(self.username)

            while not self.shutdown:
                if self.connected:
                    try:
                        message = input()
                        data = {
                            "type": "message",
                            "text": message,
                            "from": self.username
                        }
                    except KeyboardInterrupt:
                        data = {
                            "type": "leave",
                            "from": self.username
                        }

                        self.stop()

                    self.socket_server.sendto(json.dumps(data).encode(self.CHARSET), self.server)

                    self.last_sent = time.time()

            self.__main_thread__.join()

            self.connected = False

            self.socket_server.close()

        except KeyboardInterrupt:
            self.stop()
