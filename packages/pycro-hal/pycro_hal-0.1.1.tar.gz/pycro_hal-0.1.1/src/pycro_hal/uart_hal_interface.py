import serial

from .constants import Constants


# --------------------
## Handle Uart/Serial connection to the microprocessor
class UartHalInterface:
    # --------------------
    ## constructor
    def __init__(self):
        ## serial port handle
        self._ser = None

        ## port name e.g. /dev/ttyUSB0
        self._port = None

    # --------------------
    ## the serial port being used
    #
    # @return the serial port
    @property
    def port(self):
        return self._port

    # --------------------
    ## set the serial port
    #
    # @param val  the new port to use
    # @return None
    @port.setter
    def port(self, val):
        self._port = val

    # --------------------
    ## initialize.
    # open the serial port to the UART baudrate specified in Constants
    #
    # @return None
    def init(self):
        # baudrate must match Arduino's baudrate so it must be a constant
        self._ser = serial.Serial(self.port, Constants.uart_baudrate)

    # --------------------
    ## terminate.
    # close the serial port
    #
    # @return None
    def term(self):
        self._ser.close()

    # --------------------
    ## send the given packet to the microprocessor
    #
    # @param packet  the bytestring packet to send
    # @return None
    def send(self, packet):
        self._ser.write(packet)

    # --------------------
    ## recv bytes from the microprocessor
    #
    # @param size  (optional) the number of bytes to read; default 1
    # @return the bytes read (bytestring)
    def recv(self, size=1):
        ch = self._ser.read(size=size)
        return ch
