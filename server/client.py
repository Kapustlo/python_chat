class Client:
    def __init__(self, address, username = ""):
        self.address = address
        self.username = username

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def set_address(self, address):
        self.address = address
