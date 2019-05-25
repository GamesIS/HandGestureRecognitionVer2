import json
import socket

#UDP_IP = "127.0.0.1"
#UDP_PORT = 9876
def send_json(prediction, names, ip, port):
    MESSAGE = conv_to_json(prediction, names)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(bytes(MESSAGE, "utf-8"), (ip, port))
    #while True:


def conv_to_json(prediction, names):
    predict = Prediction(prediction, names)
    json_message = json.dumps(predict.__dict__, ensure_ascii=False)
    return json_message

class Prediction(object):
    def __init__(self, prediction, names):
        self.prediction = prediction.tolist()
        self.names = names

        # self.prediction.append(0.74)
        # self.prediction.append(0.25)
        # self.prediction.append(0.88)
        #
        # self.names.append("Class1")
        # self.names.append("Class2")
        # self.names.append("Class3")
