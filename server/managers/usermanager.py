import client

class UserManager:
    clients = {}

    def _add_user(self, address, username):
        self.clients[address] = client.Client(address, username)

    def _remove_user(self, address):
        del self.clients[address]

    def is_username_unique(self, username):
        copied = self.clients.copy()
        for address in copied:
            client = copied[address]
            if client.get_username() == username:
                return False

        return True

    def is_user_online(self, address):
        for client_address in self.clients.copy():
            if client_address[0] == address[0]:
                return True

        return False

    def drop_clients(self):
        self.clients = {}

    def total_clients():
        return len(self.clients.keys())
