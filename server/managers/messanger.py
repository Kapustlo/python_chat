import datetime
import json

class Messanger:
    def __init__(self, charset):
        self.CHARSET = charset

    def __prepare_message_body(self, status, message_from, text):
        return {
            "status": status,
            "from": message_from,
            "text": text,
            "date": str(datetime.datetime.utcnow())
        }

    def _prepare_response(self, status, message_from, text):
        return self.__prepare_message_body(status, message_from, text)

    def _generate_error_message(self, fatal, message_from, text = ""):
        response = self.__prepare_message_body("error", message_from, text)
        response["fatal"] = fatal

        return response

    def _wrap_response(self, data):
        return json.dumps(data).encode(self.CHARSET)

    def _parse_response_data(self, data):
        return json.loads(data.decode(self.CHARSET))
