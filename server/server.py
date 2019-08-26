import socket
import threading
import json
import datetime
import os
import time
import math

import client
import handler
import logger

DEFAULT_MAX_CONNS = 10
DEFAULT_BUF_SIZE = 1024
DEFAULT_MESSAGE_LENGTH = 32
DEFAULT_CHARSET = "utf-8"
DEFAILT_IDLE_TIME = math.inf

class Server:
    def __init__(self, address, config):
        self.address = address
        self.shutdown = True

        self.clients = {} # Keys are addresses (host:port) and values are Client objects

        self.__main_thread__ = None # Messages
        self.__secondary_thread__ = None # Connection checks

        self.start_time = None

        self.CHARSET = config.get("charset") if config.get("charset") else DEFAULT_CHARSET
        self.BUF_SIZE = config.get("buf_size") if config.get("buf_size") else DEFAULT_BUF_SIZE
        self.MAX_MESSAGE_LENGTH = config.get("max_length") if config.get("max_length") else DEFAULT_MESSAGE_LENGTH
        self.MAX_CONNS = config.get("max_conns") if config.get("max_conns") else DEFAULT_MAX_CONNS
        self.IDLE_TIME = config.get("idle_time") if config.get("idle_time") else DEFAILT_IDLE_TIME
        self.SERVER_NAME = config.get("server_name") if config.get("server_name") else ""

    def _parse_response_data(self, data):
        return json.loads(data.decode(self.CHARSET))

    def __add_user(self, address, username):
        self.clients[address] = client.Client(address, username)

    def __remove_user(self, address):
        del self.clients[address]

    def __login_user(self, parsed_data, address):

        print("{} connected".format(address))

        total_clients = len(self.clients.keys())

        if total_clients > self.MAX_CONNS:
            return handler.generate_error_message(True, "No room for you, too many users, sorry :(", self.MAX_CONNS)

        username = parsed_data["username"]

        copied = self.clients.copy()

        for client in copied:
            if copied[client].get_username() == username:
                return handler.generate_error_message(True, "{} is not a unique username".format(username))

        self.__add_user(address, username)

        text = "{} joined | users online: {}".format(username, len(self.clients.keys()))

        logger.log(text, "connections", address)

        return {
            "status": "info",
            "from": self.SERVER_NAME,
            "text": text
        }

    def __proceed_message(self, parsed_data, address):
        client = self.clients[address]
        username = client.get_username()
        print(parsed_data)
        type = parsed_data["type"]

        if type == "message":
            text = parsed_data["text"]

            if not len(text.strip()):
                return handler.generate_error_message(False, "Empty messages have no meaning, your message was not sent :)")

            if len(text) > self.MAX_MESSAGE_LENGTH:
                return handler.generate_error_message(False, "Your message is too long, maximum length is {}".format(self.MAX_MESSAGE_LENGTH))

            time_now = str(datetime.datetime.now()).split(".")[0]

            message = "{}: {}".format(username, text)

            if not client.send_message(message):
                return handler.generate_error_message(False, "Too many requests, wait before sending another one")

            print(message)

            logger.log(message, "messages", address)

            return {
                "status": "success",
                "from": username,
                "text": "[{}] {}".format(time_now, text)
            }

        elif type == "leave":
            self.__remove_user(address)

            text = "{} left | total users: {}".format(username, len(self.clients.keys()))

            logger.log(text, "connections", address)

            return {
                "status": "info",
                "from": username,
                "text": text
            }

        elif type == "join":
            user = self.clients[address]
            old_username = user.get_username()
            user.set_username(username)
            self.clients[address] = user

            text = "{} reconnected as {}".format(old_username, username)

            logger.log(text, "connections", address)

            return {
                "status": "info",
                "from": self.SERVER_NAME,
                "text": text
            }

    def __send_public_message(self, response, address, status):
        for client in self.clients.copy():
            if client != address or status == "info":
                self.server_socket.sendto(response, client)

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
                response = handler.generate_error_message(True, "Invalid data received")

            status = response["status"]

            response = json.dumps(response).encode(self.CHARSET)

            if status == "error":
                self.server_socket.sendto(response, address)
            else:
                threading.Thread(target=self.__send_public_message, args=(response, address, status), daemon=True).start()

    def stop(self):
        self.shutdown = True
        self.server_socket.close()
        self.__main_thread__.join()
        self.__secondary_thread__.join()

        self.clients = {}

        self.__main_thread__ = None
        self.__secondary_thread__ = None

        self.start_time = None

    def is_user_online(self, address):
        for client_address in self.clients.copy():
            if client_address[0] == address[0]:
                return True
        else:
            return False

    def __send_checked(self):
        while not self.shutdown:
            for address in self.clients.copy():
                client = self.clients[address]
                if time.time() - client.last_sent >= self.IDLE_TIME:
                    message = json.dumps(handler.generate_error_message(True, "You have been idle for too long", "")).encode(self.CHARSET)
                    self.__remove_user(address)
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
                result = """list - get list of all connected users"""
            elif command == "list":
                copied = self.clients.copy()
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
                result = ""
                for address in self.clients.copy():
                    self.server_socket.sendto(
                        json.dumps({
                            "status": "info",
                            "from": self.SERVER_NAME,
                            "text": " ".join(args[1:])
                        }).encode(self.CHARSET),
                        address
                    )

            elif command == "kick":
                username = args[1]
                copied = self.clients.copy()
                for address in copied:
                    client = copied[address]
                    if client.get_username() == username:
                        result = "{} ({}) has been kicked from the chat".format(client.get_username(), address)
                        self.server_socket.sendto(json.dumps(handler.generate_error_message(True, "You have been kicked from the chat")).encode(self.CHARSET), address)
                        self.__remove_user(address)
                        break
                else:
                    result = "User with the given username ({}) has not been found".format(username)

        print(result)
