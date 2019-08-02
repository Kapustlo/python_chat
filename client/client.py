import socket, threading, json, time

def get_config(path="config.json"):
    with open(path, "r") as file:
        return json.loads(file.read())

config = get_config()

server = (config["server"]["host"], config["server"]["port"])

socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_server.bind((config["host"], config["port"]))
socket_server.setblocking(0)

shutdown = False

joined = False

def get_response_text(data):
    status = data["status"]
    if status == "error":
        return "[error: {}] => {} \n".format(data["text"], data["value"])

    elif status == "success":
        username = data["from"]
        text = data["text"]

        return "[{}]: {}".format(username, text)

    return data["text"]

def parse_response_data(data):
    return json.loads(data.decode("utf-8"))

def reciever(sock):
    while not shutdown:
        try:
            while True:
                data, address = sock.recvfrom(config["buf_size"])
                print(get_response_text(parse_response_data(data)))
                time.sleep(.01)
        except:
            pass

username = input("Enter your username: ")

thread = threading.Thread(target=reciever, args=(socket_server,))
thread.start()

while not shutdown:
    if not joined:
        data = {
            "type": "join",
            "username": username,
            "from": username,
            "address": config["host"]
        }
        joined = True
    else:
        try:
            message = input("[{}]: ".format(username))
            data = {
                "type": "message",
                "text": message,
                "from": username,
                "address": config["host"]
            }
        except Exception:
            data = {
                "type": "leave",
                "from": username,
                "address": config["host"]
            }

            shutdown = True

    socket_server.sendto(json.dumps(data).encode("utf-8"), server)

thread.join()

socket_server.close()
