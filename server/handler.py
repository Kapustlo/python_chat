import json

def validate_value(value):
    if type(value) != type(""):
        value = value.decode("utf-8")

    return value

def incorrect_json(value=""):
    value = validate_value(value)
    return json.dumps({
        "status": "error",
        "text": "Invalid json format",
        "value": value
    }).encode("utf-8")

def username_not_unique(username=""):
    username = validate_value(username)
    return json.dumps({
        "status": "error",
        "text": "Username is not unique",
        "value": username
    }).encode("utf-8")

def failed_cridentials(value=""):
    return json.dumps({
        "status": "error",
        "text": "Incorrect cridentials",
        "value": value
    }).encode("utf-8")
