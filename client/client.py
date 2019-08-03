import socket
import threading
import time
import json

class Client:
    def __init__(self, address, server, config):
        self.address = address
        self.server = server

        self.config = config

        self.shutdown = True
        self.joined = False
        self.connected = False
        self.failed = False

        self.timeout = 5

    def _get_response_text(self, data):
        status = data["status"]
        if status == "error":
            return "[error: {}] => {} \n".format(data["text"], data["value"])

        else:
            username = data["from"]
            text = data["text"]

            return "[{}]: {}".format(username, text)

        return data["text"]

    def _parse_response_data(self, data):
        return json.loads(data.decode("utf-8"))

    def reciever(self, sock):
        print("Trying to connect to the server...")
        while not self.shutdown:
            while True:
                if time.time() - self.start_time >= 5 and not self.connected:
                    print("Failed to connect to the server, press 'Enter'")
                    self.stop()
                    self.failed = True
                    break
                try:
                    data, address = sock.recvfrom(self.config["buf_size"])
                    if not self.connected:
                        self.connected = True
                        print("Success")
                    print(self._get_response_text(self._parse_response_data(data)))
                except Exception as e:
                    break

    def stop(self):
        self.shutdown = True
        self.joined = False

    def run(self):
        self.username = input("Enter your nickname: ")

        self.start_time = time.time()

        print("Opening a socket...")
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_server.bind(self.address)
        self.socket_server.setblocking(0)

        self.__main_thread__ = threading.Thread(target=self.reciever, args=(self.socket_server,))
        self.__main_thread__.start()

        self.shutdown = False

        while not self.shutdown:
            if not self.joined:
                data = {
                    "type": "join",
                    "username": self.username,
                    "from": self.username,
                    "address": self.address[0]
                }
                self.joined = True
            else:
                try:
                    message = input()
                    data = {
                        "type": "message",
                        "text": message,
                        "from": self.username,
                        "address": self.address[0]
                    }
                except KeyboardInterrupt:
                    data = {
                        "type": "leave",
                        "from": self.username,
                        "address": self.address[0]
                    }

                    self.stop()


            self.socket_server.sendto(json.dumps(data).encode("utf-8"), self.server)

        self.__main_thread__.join()

        self.connected = False

        self.socket_server.close()
