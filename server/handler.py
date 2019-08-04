import json

def username_not_unique(username=""):
    return {
        "status": "error",
        "fatal": True,
        "text": "Username is not unique",
        "value": username
    }

def failed_credentials(value=""):
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

def msg_length_ecc(length=""):
    return {
        "status": "error",
        "fatal": False,
        "text": "Message is too long, maximum length is " + length,
        "value": ""
    }

def invalid_data(data):
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
