import json

def validate_value(value):
    if type(value) != type(""):
        value = value.decode("utf-8")

    return value

def incorrect_json(value=""):
    value = validate_value(value)
    return json.dumps({
        "status": "error",
        "fatal": True,
        "text": "Invalid json format",
        "value": value
    }).encode("utf-8")

def username_not_unique(username=""):
    username = validate_value(username)
    return json.dumps({
        "status": "error",
        "fatal": True,
        "text": "Username is not unique",
        "value": username
    }).encode("utf-8")

def failed_cridentials(value=""):
    value = validate_value(value)
    return json.dumps({
        "status": "error",
        "fatal": True,
        "text": "Incorrect cridentials",
        "value": value
    }).encode("utf-8")

def max_conns_ecc():
    return json.dumps({
        "status": "error",
        "fatal": True,
        "text": "Could not connect: maximum users reached",
        "value": ""
    }).encode("utf-8")
