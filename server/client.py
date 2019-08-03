import time

class Client:
    def __init__(self, address, username = ""):
        self.address = address
        self.username = username

        self.last_sent = time.time()

        self.max_messages = 40
        self.messages = 0

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def set_address(self, address):
        self.address = address

    def can_send_message(self):
        time_passed = time.time() - self.last_sent >= 5
        if time_passed:
            self.messages = 0

        if time_passed or self.messages <= self.max_messages:
            return True

        return False

    def send_message(self, message):
        can_send = self.can_send_message()

        if can_send:
            self.messages += 1
            self.last_sent = time.time()

            return True

        return False
