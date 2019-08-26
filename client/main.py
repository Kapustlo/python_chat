import json
import client
import sys

def get_config(path="config.json"):
    with open(path, "r") as file:
        return json.loads(file.read())

config = get_config()

address = ("localhost", 0)
server = (config["server"]["host"], config["server"]["port"])

def main():
    try:
        username = input("Enter your nickname: ") if len(sys.argv) < 2 else sys.argv[1]
    except KeyboardInterrupt:
        exit()

    socket = client.Client(username, address, server, config)

    socket.run()

    while not socket.failed and not socket.shutdown:
        try:
            pass
        except KeyboardInterrupt:
            socket.stop()
            break

    to_be_continued = input("Do you wish to try again? (yes/no) ").strip()

    if to_be_continued == "yes" or to_be_continued == "Yes" or to_be_continued == "YES":
        main()

if __name__ == "__main__":
    main()
