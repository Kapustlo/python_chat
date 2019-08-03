import datetime
import os

def log(message, type, address):
    time_now = str(datetime.datetime.now()).split(".")[0]
    cur_date = time_now.split(" ")[0].replace("-","_")
    file_path = "/logs/{type}/{type}_{date}.txt".format(type = type, date = cur_date)
    with open(os.getcwd() + file_path, "a") as file:
        data = "[{} | {}:{}]: {} \n".format(time_now, address[0], address[1], message)
        print(data)
        file.write(data)
