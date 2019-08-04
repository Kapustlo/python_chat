import json

def generate_error_message(fatal, text = "", value = ""):
    return {
        "status": "error",
        "fatal": fatal,
        "text": text,
        "value": value
    }
