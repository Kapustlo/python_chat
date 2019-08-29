class Messanger:
    def __init__(self, charset):
        self.CHARSET = charset

    def _parse_response_data(self, data):
        return json.loads(data.decode(self.CHARSET))

    def _wrap_message(self, data):
        return json.dumps(data).encode(self.CHARSET)
