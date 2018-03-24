import time
import random


AF_INET     = 0
SOCK_STREAM = 1
SHUT_RDWR   = 2

class socket(object):

    def __init__(self, *args, **kwars):
        print("NEW SOCKET")
        self.sent = False
        pass

    def connect(self, address):
        pass

    def close(self):
        pass

    def shutdown(self, *a, **ka):
        pass

    def recv(self, num_bytes):
        # wait = random.random() * 10 + 10
        if not self.sent:
            time.sleep(2)
            self.sent = True
        else:
            time.sleep(30)
        print("RETURNING BYTES")
        return b"message here!\r\n"

    def send(self, message):
        pass

    def bind(self, address):
        pass

    def listen(self, num):
        time.sleep(1000)

    def accept(self):
        return (self, ("192.168.0.1", 4665))




MockSocket = socket

