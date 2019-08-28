import time

from server import Server

def parse_seconds(difference):
    years = months = weeks = days = hours = minutes = seconds = milliseconds = 0

    uptime = "%.2f" % (difference)

    seconds, milliseconds = uptime.split(".")

    seconds = int(seconds)
    milliseconds = int(milliseconds)

    minutes = seconds / 60 if seconds >= 60 else 0

    minutes = int(seconds / 60)
    seconds -= minutes * 60

    hours = int(seconds / 3600)
    minutes -= hours * 60

    days = int(seconds / 86400)
    hours -= days * 24

    weeks = int(seconds / 604800)
    days -= weeks * 7

    years = int(seconds / 31536000)
    weeks -= years * 12

    return (years, months, weeks, days, hours, minutes, seconds, milliseconds)

class Chat(Server):
    def __init__(self, address, config):
        super().__init__(address, config)

    def __help(self):
        return """
list - get list of all connected users
uptime - shows server uptime
stop/restart - stops/starts/restarts server
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
        parsed_times = parse_seconds(time.time() - self.start_time)

        names = ("years", "months", "weeks", "days", "hours", "minutes", "seconds", "milliseconds")

        years, months, weeks, days, hours, minutes, seconds, milliseconds = parsed_times

        if years:
            result = "{} years, {} months".format(years, months)
        elif months:
            result = "{} months, {} weeks".format(months, weeks)
        elif weeks:
            result = "{} weeks, {} days".format(weeks, days)
        elif days:
            result = "{} days, {} hours".format(days, hours)
        else:
            result = "{}:{}:{}.{}".format(hours, minutes, seconds, milliseconds)

        return result

    def __stop(self):
        print("Stopping server...")
        self.stop()

    def __restart(self):
        print("Restarting server...")
        self.restart()

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

        if result:
            print(result)
