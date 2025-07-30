# --------------------
## holds common configuration values
class Cfg:
    # --------------------
    ## constructor
    def __init__(self):
        ## whether logging is verbose or not
        self.verbose = False

        ## the communication protocol to use with the microprocessor. valid: 'uart'
        self.protocol = 'notset'

        ## the port to use uart/serial e.g. /dev/ttyUSB0
        self.uart_port = 'notset'

    # --------------------
    ## initialize
    #
    # @return None
    def init(self):
        pass
