import time, threading, colorama, readline, sys
import msvcrt

COLS = 80
DEFAULT_IN_HANDLE_PERIOD = 1
DEFAULT_GETCH_DELAY = 0.05 #120words/min, 1200 letters per minutes,  20 letters per second: 0.05sec/l
DEFAULT_ENCODING = 'utf8'

class Interface(object):
    "Command line interface object that handles threaded input/output display."
    def __init__(self, handleIncoming, handleOutgoing, inHandlePeriod = DEFAULT_IN_HANDLE_PERIOD,
        encoding = DEFAULT_ENCODING):
        """Create an interface object and takes two methods that will be called to fetch
        incoming messages and redirect outgoing messages to."""
        self.handleIncoming = handleIncoming
        self.handleOutgoing = handleOutgoing
        self.inHandlePeriod = inHandlePeriod
        self.encoding = encoding
        self.run = False
        self.buffer = ''

    def goToStart(self):
        "Erases the input buffer lines."
        inputLength = len(self.buffer) + 3
        numInputLines = inputLength // COLS
        sys.stdout.write('\x1b[2K')
        sys.stdout.write('\x1b[1A\x1b[2K' * numInputLines)
        sys.stdout.write('\r')

    def writeStartSymbol(self):
        "Writes the default start symbol at the start of the line, without a linebreak."
        sys.stdout.write('>> ')

    def displayInputs(self):
        "Calls the incomig messages fetcher passed at creation regularly and displays its results."
        while self.run:
            messages = self.handleIncoming()
            if messages:
                self.goToStart()
            for mess in messages:
                print("<< " + mess)
            if messages:
                self.writeStartSymbol()
                sys.stdout.write(self.buffer)
            time.sleep(self.inHandlePeriod)

    def readInput(self):
        "Reads and displays one character from stdin. Returns the input buffer if CR is received."
        data = msvcrt.getch()

        #Handle Ctrl+C
        if data == b'\x03':
            raise KeyboardInterrupt

        character = data.decode(self.encoding)
        #Handle return
        if character == '\r':
            if self.buffer != '':
                message = self.buffer
                self.buffer = ''
                return message
            else:
                return

        #Add char to buffer
        self.buffer += character
        sys.stdout.write(character)

    def start(self):
        "Starts the two display loops to handle input/output."
        colorama.init()
        self.run = True
        threading.Thread(target = self.displayInputs).start()
        self.writeStartSymbol()
        while 1:
            out = self.readInput()
            if out:
                print('') #Linebreak
                self.writeStartSymbol()
                self.handleOutgoing(out)
            time.sleep(DEFAULT_GETCH_DELAY)

    def stop(self):
        "Sets flag to stop output thread."
        self.run = False
