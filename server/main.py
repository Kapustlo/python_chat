import socket, json, datetime

import chat

if __name__ == "__main__":
    with open("json/config.json", "r") as file:
        config = json.loads(file.read())

    HOST = config.get("host")
    PORT = config.get("port")

    connection_data = (HOST, PORT)

    chat_server = chat.Chat(connection_data, config)

    chat_server.start()

    while not chat_server.shutdown:
        try:
            command = input()
            if len(command.strip()):
                chat_server.command(command)
        except KeyboardInterrupt:
            chat_server.stop()
            break
