import json
import client
import socket
def get_config(path="config.json"):
    with open(path, "r") as file:
        return json.loads(file.read())

config = get_config()

address = (config["host"], config["port"])
server = (config["server"]["host"], config["server"]["port"])

def main():
    socket = client.Client(address, server, config)

    socket.run()

    while not socket.failed and not socket.shutdown:
        try:
            pass
        except KeyboardInterrupt:
            socket.stop()
            break

    print("Disconnected")

    to_be_continued = input("Do you wish to try again? (yes/no) ").strip()

    if to_be_continued == "yes" or to_be_continued == "Yes" or to_be_continued == "YES":
        main()

if __name__ == "__main__":
    main()
