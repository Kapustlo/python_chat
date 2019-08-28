import time

from server import Server

class Chat(Server):
    def __init__(self, address, config):
        super().__init__(address, config)

    def __help(self):
        return """
list - get list of all connected users
uptime - shows server uptime
stop/start/restart - stops/starts/restarts server
say *message* - sends message to everyone in the chat (* is not required)
kick *username* - kicks a user
        """

    def __list(self):
        result = "No users"

        copied = self.clients.copy()

        for index, address in enumerate(copied):
            client = copied[address]
            result += "#{}: {} {} \n".format(index + 1, client.get_username(), address)

        return result

    def __uptime(self):
        uptime = "%.2f" % (time.time() - self.start_time)
        return "{} seconds".format(uptime)

    def __stop(self):
        self.stop()
        return "Stopping server..."

    def __restart(self):
        self.restart()
        return "Restarting server..."

    def __say(self, message):
        for address in self.clients.copy():
            self.server_socket.sendto(self._wrap_response(self._prepare_response("info", self.SERVER_NAME, message)),address)

        return "[{}]: {}".format(self.SERVER_NAME, message)

    def __kick(self, username):
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

        return result

    def command(self, command):
        args = command.split(" ")
        args_length = len(args)

        command = args[0]

        result = "'{}' is an invalid command, use 'help' for help".format(command)

        if command == "help":
            result = self.__help()
        elif command == "list":
            result = self.__list()
        elif command == "uptime":
            result = self.__uptime()
        elif command == "stop":
            result = self.__stop()
        elif command == "restart":
            result = self.__restart()
        elif command == "say":
            message = " ".join(args[1:])
            result = self.__say(message)
        elif command == "kick":
            username = args[1]
            result = self.__kick(username)

        print(result)
