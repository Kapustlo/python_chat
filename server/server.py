import socket, json, datetime
from handler import Handler

def get_config(path="config.json"):
    with open(path, "r") as file:
        data = file.read()
        return json.loads(data)

def parse_response_data(data, charset):
    return json.loads(data.decode(charset))

config = get_config()

HOST = config.get("host")
PORT = config.get("port")
CHARSET = config.get("charset")
MAX_MESSAGE_LENGTH = config.get("max_length")
BUF_SIZE = config.get("buf_size")
MAX_CONNS = config.get("max_conns")

handler = Handler(CHARSET)


connection_data = (HOST, PORT)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(connection_data)

print("Server started {}".format(connection_data))

clients = {}

stop = False

while not stop:
    try:
        data, address = server_socket.recvfrom(BUF_SIZE)

        error = None

        try:
            parsed_data = parse_response_data(data, CHARSET)
        except Exception as e:
            print(e)
            server_socket.sendto(handler.incorrect_json(data), address)
            continue

        if address not in clients:
            print("{} connected".format(address))

            total_clients = len(clients.keys())

            if total_clients < MAX_CONNS:
                username = parsed_data["username"]
                came_from = parsed_data["from"]

                if username == came_from:
                    username_unique = True

                    for client in clients:
                        client_username = client["username"]

                        if client_username == username:
                            error = handler.username_not_unique(username)
                            break;

                    if username_unique:

                        clients[address] = {
                            "messages": [],
                            "username": username
                        }

                        print("{} logged in | total users: {}".format(username, len(clients.keys())))

                        message = json.dumps({
                            "status": "success",
                            "address": HOST,
                            "from": "Server",
                            "text": "{} joined".format(username)
                        })
                else:
                    error = handler.failed_cridentials()
            else:
                error = handler.max_conns_ecc()

        else:
            client = clients[address]
            username = client["username"]

            type = parsed_data["type"]

            if type == "message":
                text = parsed_data["text"]
                if len(text) <= MAX_MESSAGE_LENGTH:
                    for client in clients:
                        if client == address:
                            clients[client]["messages"].append(text)
                            time_now = str(datetime.datetime.now()).split(".")[0]
                            print("[{}] {} sent: \"{}\" | total messages: {}".format(time_now, username, text, len(clients[client]["messages"])))
                            break

                    message = json.dumps({
                        "status": "success",
                        "from": username,
                        "address": address,
                        "text": text
                    })
                else:
                    error = handler.msg_length_ecc(MAX_MESSAGE_LENGTH)

            elif type == "leave":
                del clients[address]
                print("{} left | total users: {}".format(username, len(clients.keys())))
                message = json.dumps({
                    "status": "info",
                    "from": username,
                    "address": address,
                    "text": "[Server]: {} left".format(username)
                })

        if not error:
            for client in clients:
                if client != address:
                    server_socket.sendto(message.encode(CHARSET), client)
        else:
            server_socket.sendto(error, address)

    except KeyboardInterrupt:
        stop = True

server_socket.close()
