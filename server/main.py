import socket, json, datetime

import server

def get_config(path="config.json"):
    with open(path, "r") as file:
        data = file.read()
        return json.loads(data)

if __name__ == "__main__":
    config = get_config()

    HOST = config.get("host")
    PORT = config.get("port")

    connection_data = (HOST, PORT)

    chat_server = server.Server(connection_data, config)

    chat_server.start()

    while True:
        try:
            pass
        except KeyboardInterrupt:
            chat_server.stop_server()
            break
