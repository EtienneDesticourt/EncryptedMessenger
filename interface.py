import time, threading, colorama, curses, readline, sys

COLS = 80

class Interface(object):
    def __init__(self, handleIncoming, handleOutgoing):
        #self.window = curses.initscr()
        self.run = False
        self.handleIncoming = handleIncoming
        self.handleOutgoing = handleOutgoing

    def goToStart(self):
        inputLength = len(readline.get_line_buffer()) + 3
        numInputLines = inputLength // COLS
        sys.stdout.write('\x1b[2K')
        sys.stdout.write('\x1b[1A\x1b[2K' * numInputLines)
        sys.stdout.write('\r')

    def displayInputs(self):
        while self.run:
            messages = self.handleIncoming()
            if messages:
                self.goToStart()
            for mess in messages:
                print("<< " + mess)
            if messages:
                print(">> " + readline.get_line_buffer())
            time.sleep(1)

    def start(self):
        colorama.init()
        self.run = True
        threading.Thread(target = self.displayInputs).start()
        while 1:
            out = input(">> ")
            self.handleOutgoing(out)

    def stop(self):
        self.run = False



