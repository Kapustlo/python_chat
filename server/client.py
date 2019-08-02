class Client:
    def __init__(self, address, username = ""):
        self.address = address
        self.username = username

    def get_username(self):
        return self.username
