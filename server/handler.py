import json
import datetime

def generate_error_message(fatal, text = "", value = ""):
    return {
        "status": "error",
        "fatal": fatal,
        "text": text,
        "value": value,
        "from": "Server",
        "date": str(datetime.datetime.utcnow())
    }
