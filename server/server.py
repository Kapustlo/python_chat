import socket, json
import handler

def get_config(path="config.json"):
    with open(path, "r") as file:
        data = file.read()
        return json.loads(data)

def parse_response_data(data):
    return json.loads(data.decode("utf-8"))

config = get_config()

connection_data = (config.get("host"), config.get("port"))
CHARSET = config.get("charset")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(connection_data)

print("Server started {}".format(connection_data))

clients = {}

stop = False

while not stop:
    try:
        data, address = server_socket.recvfrom(config.get("buf_size"))

        error = None

        try:
            parsed_data = parse_response_data(data)
        except Exception as e:
            print(e)
            server_socket.sendto(handler.incorrect_json(data), address)
            continue

        if address not in clients:
            print("{} connected".format(address))

            total_clients = len(clients.keys())

            if total_clients < config.get("max_conns"):
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
                            "address": config.get("host"),
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
                max_length = config.get("max_length")
                if len(text) <= max_length:
                    for client in clients:
                        if client == address:
                            clients[client]["messages"].append(text)
                            print("{} sent: \"{}\" | total messages: {}".format(username, text, len(clients[client]["messages"])))
                            break

                    message = json.dumps({
                        "status": "success",
                        "from": username,
                        "address": address,
                        "text": text
                    })
                else:
                    error = handler.msg_length_ecc(max_length)

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
                    server_socket.sendto(message.encode("utf-8"), client)
        else:
            server_socket.sendto(error, address)

    except KeyboardInterrupt:
        stop = True

server_socket.close()
