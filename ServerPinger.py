import socket

import InfoSource

class SocketPinger(InfoSource.InfoSource):
    def __init__(self):
        super(SocketPinger, self).__init__()
        self.IP = ""
        self.Port = 0
        self.Name = "Server status"
        self.StatusStr = ("UP", "DOWN")

    def __call__(self):
        Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Result = Sock.connect_ex((self.IP, self.Port))
        if Result == 0:
            self.Result = self.StatusStr[0]
        else:
            self.Result = self.StatusStr[1]
        return self.Result

    @classmethod
    def fromDict(cls, src_dict):
        Pinger = cls()
        Pinger.Name = src_dict["Name"]
        Pinger.IP = src_dict["IP"]
        Pinger.Port = src_dict["Port"]
        if "StatusStr" in src_dict:
            Pinger.StatusStr = src_dict["StatusStr"]

        return Pinger
