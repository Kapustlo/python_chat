import json

class Handler:
    def __init__(self, charset="utf-8"):
        self.charset = charset

    def validate_value(self, value):
        try:
            value = value.decode(self.charset)
        except:
            value = str(value)

        return value

    def username_not_unique(self, username=""):
        username = self.validate_value(username)
        return {
            "status": "error",
            "fatal": True,
            "text": "Username is not unique",
            "value": username
        }

    def failed_credentials(self, value=""):
        value = self.validate_value(value)
        return {
            "status": "error",
            "fatal": True,
            "text": "Incorrect credentials",
            "value": value
        }

    def max_conns_ecc(self):
        return {
            "status": "error",
            "fatal": True,
            "text": "Could not connect: maximum users reached",
            "value": ""
        }

    def msg_length_ecc(self, length=""):
        length = self.validate_value(length)
        return {
            "status": "error",
            "fatal": False,
            "text": "Message is too long, maximum length is " + length,
            "value": ""
        }

    def invalid_data(self, data):
        data = self.validate_value(data)
        return {
            "status": "error",
            "fatal": True,
            "text": "Invalid data received",
            "value": ""
        }

    def too_many_requests(self):
        return {
            "status": "error",
            "fatal": False,
            "text": "Too many requests, wait before sending another message",
            "value": ""
        }
