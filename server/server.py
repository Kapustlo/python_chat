import socket
import threading
import json
import datetime

import client
import handler

class Server:
    def __init__(self, address, config):
        self.address = address
        self.stop = True

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(address)

        self.client_increment = 0
        self.clients = {}

        self.__main_thread__ = None

        self.CHARSET = config.get("charset") if config.get("charset") else "utf-8"
        self.BUF_SIZE = config.get("buf_size") if config.get("buf_size") else 1024
        self.MAX_MESSAGE_LENGTH = config.get("max_length") if config.get("max_length") else 32
        self.MAX_CONNS = config.get("max_conns") if config.get("max_conns") else 10

        self.__handler__ = handler.Handler(self.CHARSET)

    def parse_response_data(self, data):
        return json.loads(data.decode(self.CHARSET))

    def stop_server(self):
        self.stop = True
        self.server_socket.close()
        self.__main_thread__.join()

    def is_user_online(self, address):
        for client_address in self.clients:
            if client_address[0] == address[0]:
                return True

    def __add_user(self, address, username):
        self.clients[address] = client.Client(address, username)

    def __remove_user(self, address):
        if address in self.clients:
            del self.clients[address]

    def __login_user(self, parsed_data, address):

        print("{} connected".format(address))

        total_clients = len(self.clients.keys())

        if total_clients > self.MAX_CONNS:
            return self.__handler__.max_conns_ecc()

        username = parsed_data["username"]

        for client in self.clients:
            client_username = self.clients[client].get_username()

            if client_username == username:
                return self.__handler__.username_not_unique(username)

        self.__add_user(address, username)

        print(self.clients)

        print("{} logged in | total users: {}".format(username, len(self.clients.keys())))

        return {
            "status": "info",
            "address": self.address[0],
            "from": "Server",
            "text": "{} joined".format(username)
        }

    def __proceed_message(self, parsed_data, address):
        client = self.clients[address]
        username = client.get_username()

        type = parsed_data["type"]

        if type == "message":
            text = parsed_data["text"]
            if len(text) > self.MAX_MESSAGE_LENGTH:
                return self.__handler__.msg_length_ecc(self.MAX_MESSAGE_LENGTH)

            time_now = str(datetime.datetime.now()).split(".")[0]
            print("[{}] {}: {}".format(time_now, username, text))

            return {
                "status": "success",
                "from": username,
                "address": address,
                "text": text
            }

        elif type == "leave":
            self.__remove_user(address)

            print("{} left | total users: {}".format(username, len(self.clients.keys())))

            return {
                "status": "info",
                "from": username,
                "address": address,
                "text": "[Server]: {} left".format(username)
            }

        elif type == "join":
            user = self.clients[address]
            old_username = user.get_username()
            user.set_username(username)
            self.clients[address] = user
            print(self.clients[address].get_username())
            return {
                "status": "info",
                "address": self.address[0],
                "from": "Server",
                "text": "[Server]: {} reconnected as {}".format(old_username, username)
            }

    def __send_public_message(self, response, address, status):
        for client in self.clients:
            if client != address or status == "info":
                self.server_socket.sendto(response, client)

    def __run(self):
        self.stop = False

        while not self.stop:
            data, address = self.server_socket.recvfrom(self.BUF_SIZE)

            try:
                parsed_data = self.parse_response_data(data)
                response = self.__proceed_message(parsed_data, address) if self.is_user_online(address) else self.__login_user(parsed_data, address)
            except Exception as e:
                print(e)
                response = self.__handler__.invalid_data(data)

            status = response["status"]

            response = json.dumps(response).encode(self.CHARSET)

            if status == "error":
                server_socket.sendto(response, address)
            else:
                threading.Thread(target=self.__send_public_message, args=(response, address, status), daemon=True).start()

    def start(self):
        self.__main_thread__ = threading.Thread(target = self.__run, daemon=True)
        self.__main_thread__.start()
