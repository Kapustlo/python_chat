import socket
import threading
import datetime
import time
import math

import logger

from managers.messanger import Messanger
from managers.usermanager import UserManager

DEFAULT_MAX_CONNS = 10
DEFAULT_BUF_SIZE = 1024
DEFAULT_MESSAGE_LENGTH = 32
DEFAULT_CHARSET = "utf-8"
DEFAILT_IDLE_TIME = math.inf

class Server(Messanger, UserManager):
    def __init__(self, address, config):
        super().__init__(config.get("charset") if config.get("charset") else DEFAULT_CHARSET)

        self.address = address
        self.shutdown = True

        self.start_time = self.__secondary_thread__ = self.__main_thread__ = None

        self.BUF_SIZE = config.get("buf_size") if config.get("buf_size") else DEFAULT_BUF_SIZE
        self.MAX_MESSAGE_LENGTH = config.get("max_length") if config.get("max_length") else DEFAULT_MESSAGE_LENGTH
        self.MAX_CONNS = config.get("max_conns") if config.get("max_conns") else DEFAULT_MAX_CONNS
        self.IDLE_TIME = config.get("idle_time") if config.get("idle_time") else DEFAILT_IDLE_TIME
        self.SERVER_NAME = config.get("server_name") if config.get("server_name") else ""

    def __send_public_message(self, response, address, status):
        for client in self.clients.copy():
            if client != address or status == "info":
                self.server_socket.sendto(response, client)

    def __proceed_message(self, parsed_data, address):
        client = self.clients[address]
        username = client.get_username()
        type = parsed_data["type"]

        if type == "message":
            text = parsed_data["text"]

            if not len(text.strip()):
                return self._generate_error_message(False, self.SERVER_NAME, "Empty messages have no meaning, your message was not sent :)")

            if len(text) > self.MAX_MESSAGE_LENGTH:
                return self._generate_error_message(False, self.SERVER_NAME, "Your message is too long, maximum length is {}".format(self.MAX_MESSAGE_LENGTH))

            time_now = str(datetime.datetime.now()).split(".")[0]

            message = "{}: {}".format(username, text)

            if not client.send_message(message):
                return self._generate_error_message(False, self.SERVER_NAME, "Too many requests, wait before sending another one")

            print(message)

            logger.log(message, "messages", address)

            return self._prepare_response("success", username, "[{}] {}".format(time_now, text))

        elif type == "leave":
            self._remove_user(address)

            text = "{} left | total users: {}".format(username, self.total_clients())

            logger.log(text, "connections", address)

            return self._prepare_response("info", username, text)

        elif type == "join":
            old_username = client.get_username()
            user.set_username(username)
            self.clients[address] = client

            text = "{} reconnected as {}".format(old_username, username)

            logger.log(text, "connections", address)

            return self._prepare_response("info", self.SERVER_NAME, text)

    def __run(self):
        self.shutdown = False

        while not self.shutdown:
            try:
                data, address = self.server_socket.recvfrom(self.BUF_SIZE)
            except:
                continue

            try:
                parsed_data = self._parse_response_data(data)
                is_online = self.is_user_online(address)
                if is_online and not address in self.clients:
                    response = self._generate_error_message(True, self.SERVER_NAME, "You are already logged in")
                elif is_online:
                    response = self.__proceed_message(parsed_data, address)
                else:
                    response = self.__login_user(parsed_data, address)

            except Exception as e:
                print(e)
                response = self._generate_error_message(True, self.SERVER_NAME, "Invalid data received")

            status = response["status"]

            response = self._wrap_response(response)

            if status == "error":
                self.server_socket.sendto(response, address)
            else:
                threading.Thread(target=self.__send_public_message, args=(response, address, status), daemon=True).start()

    def __login_user(self, parsed_data, address):

        print("{} connected".format(address))

        total_clients = self.total_clients()

        if total_clients > self.MAX_CONNS:
            return self._generate_error_message(True, self.SERVER_NAME, "No room for you, too many users, sorry :(", self.MAX_CONNS)

        username = parsed_data["username"]

        if not len(username.strip()):
            return self._generate_error_message(True, self.SERVER_NAME, "Username must not be empty")

        copied = self.clients.copy()

        if not self.is_username_unique(username):
            return self._generate_error_message(True, self.SERVER_NAME, "{} is not a unique username".format(username))

        self._add_user(address, username)

        text = "{} joined | users online: {}".format(username, self.total_clients())

        logger.log(text, "connections", address)

        return self._prepare_response("info", self.SERVER_NAME, text)

    def __send_checked(self):
        while not self.shutdown:
            copied = self.clients.copy()
            for address in copied:
                client = copied[address]
                if time.time() - client.last_sent >= self.IDLE_TIME:
                    message = self._wrap_response(self._generate_error_message(True, self.SERVER_NAME, "You have been idle for too long"))
                    self._remove_user(address)
                else:
                    message = b'1'

                self.server_socket.sendto(message, address)

            time.sleep(1)

    def stop(self):
        self.shutdown = True
        self.server_socket.close()
        self.__main_thread__.join()
        self.__secondary_thread__.join()

        self.drop_clients()

        self.__main_thread__ = None
        self.__secondary_thread__ = None

        self.start_time = None

        print("Server stopped")

    def start(self):
        address = self.address

        ip, port = address

        if ip == "localhost":
            ip = "127.0.0.1"

        print("Starting server...")

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(address)

        self.__main_thread__ = threading.Thread(target = self.__run, daemon=True)
        self.__main_thread__.start()

        self.__secondary_thread__ = threading.Thread(target = self.__send_checked, daemon = True)
        self.__secondary_thread__.start()

        self.start_time = time.time()

        print("Server started ({}:{})".format(ip, port))

    def restart(self):
        self.stop()
        self.start()
        print("Server restarted")
