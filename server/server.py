import socket
import threading
import json
import datetime
import time
import math

import logger

from messanger import Messanger
from usermanager import UserManager

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

        self.__main_thread__ = None # Messages
        self.__secondary_thread__ = None # Connection checks

        self.start_time = None

        self.BUF_SIZE = config.get("buf_size") if config.get("buf_size") else DEFAULT_BUF_SIZE
        self.MAX_MESSAGE_LENGTH = config.get("max_length") if config.get("max_length") else DEFAULT_MESSAGE_LENGTH
        self.MAX_CONNS = config.get("max_conns") if config.get("max_conns") else DEFAULT_MAX_CONNS
        self.IDLE_TIME = config.get("idle_time") if config.get("idle_time") else DEFAILT_IDLE_TIME
        self.SERVER_NAME = config.get("server_name") if config.get("server_name") else ""

    def _parse_response_data(self, data):
        return json.loads(data.decode(self.CHARSET))

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

            text = "{} left | total users: {}".format(username, len(self.clients.keys()))

            logger.log(text, "connections", address)

            return self._prepare_response("info", username, text)

        elif type == "join":
            user = self.clients[address]
            old_username = user.get_username()
            user.set_username(username)
            self.clients[address] = user

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
                response = self.__proceed_message(parsed_data, address) if self.is_user_online(address) else self.__login_user(parsed_data, address)
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

        total_clients = len(self.clients.keys())

        if total_clients > self.MAX_CONNS:
            return self._generate_error_message(True, self.SERVER_NAME, "No room for you, too many users, sorry :(", self.MAX_CONNS)

        username = parsed_data["username"]

        copied = self.clients.copy()

        for client in copied:
            if copied[client].get_username() == username:
                return self._generate_error_message(True, self.SERVER_NAME, "{} is not a unique username".format(username))

        self._add_user(address, username)

        text = "{} joined | users online: {}".format(username, len(self.clients.keys()))

        logger.log(text, "connections", address)

        return self._prepare_response("info", self.SERVER_NAME, text)

    def stop(self):
        self.shutdown = True
        self.server_socket.close()
        self.__main_thread__.join()
        self.__secondary_thread__.join()

        self.clients = {}

        self.__main_thread__ = None
        self.__secondary_thread__ = None

        self.start_time = None

    def __send_checked(self):
        while not self.shutdown:
            copied = self.clients.copy()
            for address in copied:
                client = copied[address]
                if time.time() - client.last_sent >= self.IDLE_TIME:
                    message = self._wrap_response(self._generate_error_message(True, self.SERVER_NAME, "You have been idle for too long", ""))
                    self._remove_user(address)
                else:
                    message = b'1'

                self.server_socket.sendto(message, address)

            time.sleep(1)

    def start(self):
        print("Starting server {}:{}".format(self.address[0], self.address[1]))

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(self.address)

        self.__main_thread__ = threading.Thread(target = self.__run, daemon=True)
        self.__main_thread__.start()

        self.__secondary_thread__ = threading.Thread(target = self.__send_checked, daemon = True)
        self.__secondary_thread__.start()

        self.start_time = time.time()

    def restart(self):
        self.stop()
        self.start()

    def command(self, command):
        args = command.split(" ")
        args_length = len(args)

        result = "'{}' is an invalid command, use 'help' for help".format(command)

        if args_length == 1:
            if command == "help":
                result = """
list - get list of all connected users
uptime - shows server uptime
stop/start/restart - stops/starts/restarts server
say *message* - sends message to everyone in the chat (* is not required)
kick *username* - kicks a user
                """
            elif command == "list":
                copied = self.clients.copy()
                if not len(copied):
                    result = "No users"

                for index, address in enumerate(copied):
                    client = copied[address]
                    result += "#{}: {} {} \n".format(index + 1, client.get_username(), address)

            elif command == "uptime":
                uptime = "%.2f" % (time.time() - self.start_time)
                result = "{} seconds".format(uptime)
            elif command == "stop":
                result = "Stopping server..."
                self.stop()
            elif command == "restart":
                result = "Restarting server..."
                self.restart()

        else:
            command = args[0]

            if command == "say":
                message = " ".join(args[1:])
                result = "[{}]: {}".format(self.SERVER_NAME, message)
                for address in self.clients.copy():
                    self.server_socket.sendto(self._wrap_response(self._prepare_response("info", self.SERVER_NAME, message)),address)

            elif command == "kick":
                username = args[1]
                copied = self.clients.copy()
                for address in copied:
                    client = copied[address]
                    if client.get_username() == username:
                        result = "{} ({}) has been kicked from the chat".format(client.get_username(), address)
                        self.server_socket.sendto(self._wrap_response(self._generate_error_message(True, self.SERVER_NAME, "You have been kicked from the chat")), address)
                        self._remove_user(address)
                        break
                else:
                    result = "User with the given username ({}) has not been found".format(username)

        print(result)
