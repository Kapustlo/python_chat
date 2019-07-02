import socket, threading, json, time, config

server = (config.SERVER["host"], config.SERVER["port"])

socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_server.bind((config.HOST, config.PORT))
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
                data, address = sock.recvfrom(config.BUF_SIZE)
                print(get_response_text(parse_response_data(data)))
                time.sleep(.1)
        except:
            pass

username = input("Enter your username: ")

r = threading.Thread(target=reciever, args=(socket_server,))
r.start()

while not shutdown:
    if not joined:
        message = json.dumps({
            "type": "join",
            "username": username,
            "from": username,
            "address": config.HOST
        })
        socket_server.sendto(message.encode("utf-8"), server)
        joined = True
        time.sleep(.1)
    else:
        try:
            message = input("[{}]: ".format(username))
            message = json.dumps({
                "type": "message",
                "text": message,
                "from": username,
                "address": config.HOST
            })
            socket_server.sendto(message.encode("utf-8"), server)
        except KeyboardInterrupt:
            message = json.dumps({
                "type": "leave",
                "from": username,
                "address": config.HOST
            })

            socket_server.sendto(message.encode("utf-8"), server)

            shutdown = True

r.join()

socket_server.close()
