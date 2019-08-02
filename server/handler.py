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

    def incorrect_json(self, value=""):
        value = self.validate_value(value)
        return json.dumps({
            "status": "error",
            "fatal": True,
            "text": "Invalid json format",
            "value": value
        }).encode(self.charset)

    def username_not_unique(self, username=""):
        username = self.validate_value(username)
        return json.dumps({
            "status": "error",
            "fatal": True,
            "text": "Username is not unique",
            "value": username
        }).encode(self.charset)

    def failed_credentials(self, value=""):
        value = self.validate_value(value)
        return json.dumps({
            "status": "error",
            "fatal": True,
            "text": "Incorrect credentials",
            "value": value
        }).encode(self.charset)

    def max_conns_ecc(self):
        return json.dumps({
            "status": "error",
            "fatal": True,
            "text": "Could not connect: maximum users reached",
            "value": ""
        }).encode(self.charset)

    def msg_length_ecc(self, length=""):
        length = validate_value(length)
        return json.dumps({
            "status": "error",
            "fatal": False,
            "text": "Message is too long, maximum length is " + length,
            "value": ""
        }).encode(self.charset)

    def invalid_data(self):
        return json.dumps({
            "status": "error",
            "fatal": True,
            "text": "Invalid data received",
            "value": ""
        }).encode(self.charset)
