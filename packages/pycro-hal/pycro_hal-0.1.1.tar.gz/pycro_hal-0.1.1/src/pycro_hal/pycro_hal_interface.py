import queue
import threading
import time
from dataclasses import dataclass

from falcon_logger import FalconLogger

from .cfg import Cfg
from .constants import Constants
from .svc import svc
from .uart_hal_interface import UartHalInterface


# --------------------
## private class; a pin's modes e.g. INPUT, OUTPUT etc
class _PinMode:
    # --------------------
    ## constructor
    #
    # @param name  the pin mode name
    # @param val   the pin mode value
    def __init__(self, name, val):
        ## the pin mode's name
        self._name = name
        ## the pin mode value (0x0, 0x1, 0x2)
        self._val = val

    # --------------------
    ## convert the id to a byte stream with length and order (big/little)
    #
    # @param length  the length of the byte stream
    # @param order   either "big" or "little"
    # @return requested bytestream
    def to_bytes(self, length, order):
        return self._val.to_bytes(length, order)

    # --------------------
    ## return a printable value
    #
    # @return the name of the pin mode
    def __repr__(self):
        return self._name


# --------------------
## holds all the modes a Pin can be set to
@dataclass(frozen=True)
class PinMode:
    # pylint: disable=invalid-name
    ## digital INPUT mode; user must provide a pullup resistor
    INPUT = _PinMode('INPUT', 0x0)
    ## OUTPUT mode: pin sets to HIGH or LOW
    OUTPUT = _PinMode('OUTPUT', 0x1)
    ## digital INPUT_PULLUP mode; uses internal pullup resistor
    INPUT_PULLUP = _PinMode('INPUT_PULLUP', 0x2)


# --------------------
## private class; a pin's level e.g. HIGH or LOW
class _PinLevel:
    # --------------------
    ## constructor
    #
    # @param name  the pin level name
    # @param val   the pin level value
    def __init__(self, name, val):
        ## the pin level name LOW or HIGH
        self._name = name
        ## the pin level value (0x0, 0x1)
        self._val = val

    # --------------------
    ## convert the id to a byte stream with length and order (big/little)
    #
    # @param length  the length of the byte stream
    # @param order   either "big" or "little"
    # @return requested bytestream
    def to_bytes(self, length, order):
        return self._val.to_bytes(length, order)

    # --------------------
    ## return a printable value
    #
    # @return the name of the pin value
    def __repr__(self):
        return self._name


# --------------------
## holds all the levels a Pin can take
@dataclass(frozen=True)
class PinLevel:
    # pylint: disable=invalid-name
    ## OUTPUT pin is at 0V or being set to 0V
    LOW = _PinLevel('LOW', 0x0)
    ## OUTPUT pin is at 5V or being set to 5V
    HIGH = _PinLevel('HIGH', 0x1)


# --------------------
## Hardware Abstraction Interface to the microprocessor
class PycroHalInterface:

    # --------------------
    ## constructor
    def __init__(self):
        svc.cfg = Cfg()
        svc.cfg.init()
        svc.log = FalconLogger(mode='null')

        ## the communications thread to use
        self._thread = None
        ## the communications interface to use
        self._interface = None
        ## flag indicating the communications is done
        self._done = False
        ## queue of incoming responses from the microprocessor
        self._responses = queue.Queue()

        ## supply voltage used for the microprocessor; used for accurate ADC calculations
        self._supply_voltage = 5.000

    # --------------------
    ## get the module version
    #
    # @return version
    @property
    def version(self):
        return Constants.version

    # --------------------
    ## set the logger to use
    #
    # @param logger  reference to the logger to use
    # @return None
    def set_logger(self, logger):
        svc.log = logger

    # --------------------
    ## set the logger to LoggerNull
    #
    # @return None
    def clear_logger(self):
        svc.log = FalconLogger(mode='null')

    # --------------------
    ## access to the local Cfg object
    #
    # @return reference to the local Cfg object
    @property
    def cfg(self):
        return svc.cfg

    # --------------------
    ## initialize and start the communications interface to the microprocessor.
    #
    # @return None
    def start(self):
        self._load_protocol()
        self._interface.init()

        self._thread = threading.Thread(target=self._read_responses)
        self._thread.daemon = True
        self._thread.start()
        # wait for thread to start
        time.sleep(0.200)

        self._check_comms()

    # --------------------
    ## check communications. Should be two comm_ok packets sent.
    #
    # @return None
    def _check_comms(self):
        svc.log.line('checking communications...')
        comm_ok = 0
        count = 0
        comm_ok_needed = 2
        while count < 30 and comm_ok < comm_ok_needed:
            # can take around a second to receive the first one
            rsp = self.recv(timeout=0.100)
            if rsp is None:
                pass
            elif rsp[0] == 0x00:
                comm_ok += 1
                svc.log.line(f'comm_ok: {comm_ok}')
            count += 1
        svc.log.check(comm_ok >= 2, f'connection: {comm_ok} comm_ok rsp received; {count} loops')
        if comm_ok < 2:
            svc.abort(f'connection failed: {count} loops, but {comm_ok} rsp received (need {comm_ok_needed})')

    # --------------------
    ## stop communications with the microprocessor
    def stop(self):
        self._done = True

        self._interface.term()

    # --------------------
    ## get the last response from the queue
    #
    # @param timeout  how long to wait on an empty queue
    # @return rsp     the last response (bytestring) or None if no response received in the timeout period
    def recv(self, timeout=1.0):
        try:
            rsp = self._responses.get(block=True, timeout=timeout)
        except queue.Empty:
            rsp = None

        return rsp

    # --------------------
    ## return the supply voltage used in ADC calculations.
    #
    # @return the supply voltage
    @property
    def supply_voltage(self):
        return self._supply_voltage

    # --------------------
    ## set the supply voltage to use in ADC calculations.
    #
    # @param val   the value (volts) to use, e.g. 4.968
    # @return None
    @supply_voltage.setter
    def supply_voltage(self, val):
        self._supply_voltage = val

    # --------------------
    ## get an pin object based on the given name (str) e.g. "D10" or "LED" or "A7"
    #
    # @param name  the pin's name
    # @return None if invalid name, otherwise a DigitalPin or AnalogPin object
    def get_pin(self, name):
        name = name.upper().strip()
        if len(name) < 2:
            svc.log.bug(f'Invalid pin name: "{name}", must be "Dn" or "An"')
            return None

        # special case for built-in LED
        if name == 'LED':
            name = 'D13'

        prefix = name[0]
        if prefix not in ['D', 'A']:
            svc.log.bug(f'Invalid pin name: {name}, must start with "D" or "A"')
            return None

        pinid = int(name[1:])

        if prefix == 'D':
            # digital pin
            if pinid < 2 or pinid > 13:
                svc.log.bug(f'Invalid digital pin: {pinid}, expected LED or D2 - D13')
                return None

            pin = PycroHalInterface._DigitalPin(self, pinid)
        else:
            # analog pin
            if pinid < 0 or pinid > 7:
                svc.log.bug(f'Invalid analog pin: {pinid}, expected A0 - A7')
                return None

            pin = PycroHalInterface._AnalogPin(self, pinid)

        # uncomment to debug
        # svc.log.dbg(f'prefix: "{prefix} id:"{pinid}" pin:{pin}')

        return pin

    # === commands & responses

    # --------------------
    ## send ping cmd to the microprocessor.
    # expect a pong rsp
    #
    # @return None
    def ping(self):
        # * byte0: length = 3 bytes
        # * byte1: cmd bits TODO define these bits
        # * byte2: cmd = 0x00
        cmd = b'\x03\x00\x00'
        self._interface.send(cmd)
        svc.log.hex(cmd, 'tx:')

    # --------------------
    ## send GPIO mode cmd to the microprocessor.
    # expect no response
    #
    # @param pin   the GPIO pin to set the mode on
    # @param mode  the mode to set: INPUT (0x0) or OUTPUT (0x1)
    # @return None
    def gpio_mode(self, pin, mode):
        # * byte0: length = 5 bytes
        # * byte1: cmd bits TODO
        # * byte2: cmd = 0x01
        # * byte3: pin : the pin number e.g. 0x0D = 13 for the LED gpio
        # * byte4: state : INPUT (0x0) or OUTPUT (0x1)
        cmd = b'\x05\x00\01'
        cmd += pin.to_bytes(1, 'big')
        cmd += mode.to_bytes(1, 'big')
        self._interface.send(cmd)
        svc.log.hex(cmd, 'tx:')

    # --------------------
    ## send GPIO state cmd to the microprocessor.
    # expect no response
    #
    # @param pin    the GPIO pin to set the state on
    # @param state  the state to set: LOW (0x0) or HIGH (0x1)
    # @return None
    def gpio_write(self, pin, state):
        # * byte0: length = 5 bytes
        # * byte1: cmd bits TODO
        # * byte2: cmd = 0x02
        # * byte3: pin : the pin number e.g. 0x0D = 13 for the LED gpio
        # * byte4: state : LOW (0x0) or HIGH (0x1)
        cmd = b'\x05\x00\02'
        cmd += pin.to_bytes(1, 'big')
        cmd += state.to_bytes(1, 'big')
        self._interface.send(cmd)
        svc.log.hex(cmd, 'tx:')

    # --------------------
    ## send read GPIO state cmd to the microprocessor.
    # expect the GPIO state response
    #
    # @param pin    the GPIO pin to read
    # @return None
    def gpio_read(self, pin):
        # * byte0: length = 4 bytes
        # * byte1: cmd bits TODO
        # * byte2: cmd = 0x03
        # * byte3: pin : the pin number e.g. 0x0A = 10
        cmd = b'\x04\x00\03'
        cmd += pin.to_bytes(1, 'big')
        self._interface.send(cmd)
        svc.log.hex(cmd, 'tx:')

    # --------------------
    ## send read ADC value cmd to the microprocessor.
    #
    # @param pin    the analog pin to read
    # @return None
    def adc_read(self, pin):
        # * byte0: length = 4 bytes
        # * byte1: cmd bits TODO
        # * byte2: cmd = 0x04
        # * byte3: pin : the pin number e.g. 0x00 = A0
        cmd = b'\x04\x00\04'
        cmd += pin.to_bytes(1, 'big')
        self._interface.send(cmd)
        svc.log.hex(cmd, 'tx:')

    # --------------------
    ## convert the ADC value in the ADC response to a voltage
    #
    # @param rsp  the incoming response packet
    # @return voltage read on the ADC pin
    def adc_to_voltage(self, rsp):
        # uncomment to debug
        # svc.log.hex(rsp, 'rsp:')
        val_bytes = rsp[3:]
        # svc.log.hex(val_bytes, 'val_bytes:')
        val = int.from_bytes(val_bytes, 'little')
        # svc.log.dbg(f'val   : 0x{val:04X}={val} V/count:{self._supply_voltage / 1023.0:<0.6f}')
        voltage = val * (self._supply_voltage / 1023.0)
        return voltage

    # --------------------
    ## send ping cmd to the microprocessor.
    # expect a pong rsp
    #
    # @return None
    def uctrl_version(self):
        # * byte0: length = 3 bytes
        # * byte1: cmd bits TODO define these bits
        # * byte2: cmd = 0x05
        cmd = b'\x03\x00\x05'
        self._interface.send(cmd)
        svc.log.hex(cmd, 'tx:')

        rsp = self.recv()
        raw_type = rsp[3]
        match raw_type:
            case 0:
                uctrl_type = 'Arduino Nano'  # Atmega 328P
            case _:
                uctrl_type = f'unknown: {raw_type}'

        # byte4 is reserved
        # version is 8 characters starting at byte5
        uctrl_version = rsp[5:].decode('utf-8').rstrip()
        return uctrl_type, uctrl_version

    # --------------------
    ## get the Port b and Port D content i.e. all digital ports
    #
    # @return None
    def digital_port_read(self):
        # * byte0: length = 3 bytes
        # * byte1: cmd bits - reserved
        # * byte2: cmd = 0x06
        cmd = b'\x03\x00\x06'
        self._interface.send(cmd)
        svc.log.hex(cmd, 'tx:')

    # --------------------
    ## convert an integer into a 16 item array of 1 and 0's.
    # The returned 1 and 0 can be indexed by the bit number e.g. bit 3 can be accessed by bits[3]
    #
    # @param rawbits the 16-bit integer to convert
    # @return a 16 item array containing 1 or 0 for each bit in rawbits
    def bitarray16(self, rawbits):
        return [rawbits >> i & 1 for i in range(0, 15)]

    # --------------------
    ## read the digital ports state, wait for response and return all values is a bit array and a 16-bit integer.
    #
    # @return bits is an array of 1,0's corresponding to the bits of the integer, raw_bits is a 16-bit integer
    def all_digital_state(self):
        self.digital_port_read()
        rsp = self.recv()
        raw_bits = int.from_bytes(rsp[3:], 'big')
        bits = self.bitarray16(raw_bits)
        return bits, raw_bits

    # --------------------
    ## set up pin for PWM
    #
    # @param pin         the pin to use
    # @param duty_cycle  the duty_cycle to set to
    # @return None
    def pwm(self, pin, duty_cycle):
        valid = [3, 5, 6, 9, 10, 11]
        if pin not in valid:
            svc.log.bug(f'Invalid pin for PWM, must be one of {valid}, actual: {pin}')
            svc.abort('invalid PWM pin')

        if not isinstance(duty_cycle, int):
            svc.log.bug(f'PWM duty cycle must be an integer, actual: {type(duty_cycle)}')
            svc.abort('invalid PWM pin')

        if duty_cycle < 0 or duty_cycle > 255:
            svc.log.bug(f'PWM duty cycle must be 0 to 255, actual: {duty_cycle}')
            svc.abort('invalid PWM pin')

        # * byte0: length = 5 bytes
        # * byte1: cmd bits - reserved
        # * byte2: cmd = 0x07
        # * byte3: pin number
        # * byte4: duty cycle = 0 - 255
        cmd = b'\x05\x00\x07'
        cmd += pin.to_bytes(1, 'big')
        cmd += duty_cycle.to_bytes(1, 'big')
        self._interface.send(cmd)
        svc.log.hex(cmd, 'tx:')

    # --------------------
    ## set up a pin for controlling a servo
    #
    # @param pin    the pin to use
    # @return None
    def servo_cfg(self, pin):
        valid = [3, 5, 6, 9, 10, 11]
        if pin not in valid:
            svc.log.bug(f'Invalid pin for PWM, must be one of {valid}, actual: {pin}')
            svc.abort('invalid PWM pin')

        # byte0:  length = 4 bytes
        # byte1: cmd bits - reserved
        # byte2: cmd = 0x08
        # byte3: pin : the pin number e.g. 0x03 = D3 |
        cmd = b'\x04\x00\x08'
        cmd += pin.to_bytes(1, 'big')
        self._interface.send(cmd)
        svc.log.hex(cmd, 'tx:')

    # --------------------
    ## write a value to the servo
    #
    # @param val   the value to write
    # @return None
    def servo_write(self, val):
        # byte0:  length = 5 bytes
        # byte1: cmd bits - reserved
        # byte2: cmd = 0x09
        # byte3: LSB position e.g. 1000
        # byte4: MSB position pulse-width e.g. 1000
        cmd = b'\x05\x00\x09'
        cmd += val.to_bytes(2, 'big')
        self._interface.send(cmd)
        svc.log.hex(cmd, 'tx:')

    # --------------------
    ## send an adhoc cmd to the microprocessor
    #
    # @param usercmd  the outgoing packet
    # @return None
    def adhoc(self, usercmd):
        # * type: directive
        # * byte0: length = N bytes (3 <= N <= 255)
        # * byte1: cmd bits TODO
        # * byte2: cmd = 0xFF
        # * byte 3 to byte 255: depends on ad hoc command
        length = 3 + len(usercmd)
        cmd = b''
        cmd += length.to_bytes(1, 'big')
        cmd += b'\x00\xFF'
        if len(usercmd) > 0:
            cmd += usercmd
        self._interface.send(cmd)
        svc.log.hex(cmd, 'tx:')

    # --------------------
    ## the thread function to read all incoming responses.
    # each incoming packet has a length and once that number of bytes is read
    # the packet is saved in the response queue.
    #
    # @return None
    def _read_responses(self):
        in_packet = False
        rsp = b''
        exp_length = 0
        curr_length = 0
        while not self._done:
            # get the next byte
            ch = self._interface.recv(1)

            if self._done:
                svc.log.dbg('done')
                break

            # if we got nothing from the Arduino, connection is broken
            if not ch:
                break

            # uncomment to debug
            # svc.log.dbg(f'rsp ch: {ch}')

            if not in_packet:
                in_packet = True
                exp_length = int.from_bytes(ch, 'big')
                # svc.log.dbg(f'rx: expected len: {exp_length}')
                rsp = ch
                if exp_length == 0:
                    # special case for junk bytes
                    curr_length = 0
                else:
                    curr_length = 1
            else:
                rsp += ch
                curr_length += 1
                # svc.log.dbg(f'rx: exp:{exp_length} curr:{curr_length} {ch}')

            if curr_length == exp_length:
                svc.log.hex(rsp, 'rx:')
                self._responses.put(rsp)
                rsp = b''
                in_packet = False
                curr_length = 0
                exp_length = 0

        # TODO replace; so caller can use it to know it's disconnected
        self._responses.put('exitthread')
        svc.log.dbg('exiting thread')

    # --------------------
    ## load the correct HAL interface class for the given communication protocol.
    # if the protocol is not recognized, the app is aborted.
    #
    # @return None
    def _load_protocol(self):
        if svc.cfg.protocol == 'uart':
            self._interface = UartHalInterface()
            self._interface.port = svc.cfg.uart_port
            self._interface.baudrate = Constants.uart_baudrate
        else:
            svc.abort(f'Unknown communication protocol: "{svc.cfg.protocol}"')

    # --------------------
    ## interface for Digital pins
    class _DigitalPin:
        # --------------------
        ## constructor
        #
        # @param parent   reference to PycroHalInterface
        # @param pinid    which digital pin: 0x2 to 0xD
        def __init__(self, parent, pinid):
            ## holds reference to PycroHalInterface
            self._parent = parent
            ## holds pinid 0x2 (=D2) to 0xD (=D13)
            self._id = pinid
            ## holds last state set or run: LOW or HIGH
            self._state = None
            ## holds pin mode: input/output
            self._mode = ''
            ## holds the duty cycle to use for PWM pins
            self._duty_cycle = None

        # --------------------
        ## the Pin's id (e.g. 13)
        #
        # @return  pin id
        @property
        def id(self):
            return self._id

        # --------------------
        ## returns the last state set or run (LOW or HIGH)
        #
        # @return  the last state
        @property
        def state(self):
            return self._state

        # --------------------
        ## returns the last duty_cycle set on the pin (assumes PWM)
        #
        # @return  the last duty_cycle
        @property
        def duty_cycle(self):
            return self._duty_cycle

        # --------------------
        ## set pin mode to INPUT_PULLUP
        #
        # @return None
        def set_mode_input_pullup(self):
            self._parent.gpio_mode(self._id, PinMode.INPUT_PULLUP)
            # can't write to an input pin
            self._mode = 'input'
            ## see self._bad_func for doc
            setattr(self, 'write_low', self._bad_func)
            setattr(self, 'write_high', self._bad_func)

        # --------------------
        ## set pin mode to INPUT
        #
        # @return None
        def set_mode_input(self):
            self._parent.gpio_mode(self._id, PinMode.INPUT)
            # can't write to an input pin
            self._mode = 'input'
            setattr(self, 'write_low', self._bad_func)
            setattr(self, 'write_high', self._bad_func)

        # --------------------
        ## read the pin state.
        # up to caller to handler response
        #
        # @return None
        def read(self):
            self._parent.gpio_read(self._id)

        # --------------------
        ## read the pin state, waits for response and sets state
        #
        # @return None
        def read_state(self):
            self.read()
            rsp = self._parent.recv()
            self._state = rsp[2]

        # --------------------
        ## set pin mode to OUTPUT
        #
        # @return None
        def set_mode_output(self):
            self._parent.gpio_mode(self._id, PinMode.OUTPUT)
            # can't read an output pin
            self._mode = 'output'
            setattr(self, 'read', self._bad_func)
            setattr(self, 'read_state', self._bad_func)

        # --------------------
        ## set output pin to LOW.
        # sets state to LOW
        #
        # @return None
        def write_low(self):
            self._state = PinLevel.LOW
            self._parent.gpio_write(self._id, self._state)

        # --------------------
        ## set output pin to HIGH.
        # sets state to HIGH
        #
        # @return None
        def write_high(self):
            self._state = PinLevel.HIGH
            self._parent.gpio_write(self._id, self._state)

        # --------------------
        ## set PWM on the output pin.
        # sets duty_cycle to the given value
        #
        # @param duty_cycle  the duty cycle to use for the PWM
        # @return None
        def pwm(self, duty_cycle):
            self._duty_cycle = duty_cycle
            self._parent.pwm(self._id, self._duty_cycle)

        # --------------------
        ## configure servo mode
        #
        # @return None
        def servo_cfg(self):
            self._parent.servo_cfg(self._id)

        # --------------------
        ## set servo to uSecond value
        #
        # @param val  the value to use
        # @return None
        def servo_write_us(self, val):
            # NANO default is 544 - 2400 uS
            if val < 544:
                svc.log.bug(f'servo_write_us: min uS is 544: {val}')
                return
            if val > 2400:
                svc.log.bug(f'servo_write_us: max uS is 2400: {val}')
                return

            self._parent.servo_write(val)

        # --------------------
        ## redirect for functions that are not valid given
        # the pin's current mode e.g. should not read a pin in OUTPUT mode.
        #
        # @return None
        def _bad_func(self):
            svc.log.bug(f'bad_func: {self._mode} mode does not support that call')

        # --------------------
        ## return human readable pin ID e.g. "D10".
        # D13 is returned as "LED"
        #
        # @return the pin id as a string.
        def __repr__(self):
            if self._id == 13:
                return 'LED'
            return f'D{self._id}'

    # --------------------
    ## interface for Analog pins
    class _AnalogPin:
        # --------------------
        ## constructor
        #
        # @param parent   reference to PycroHalInterface
        # @param pinid    which analog pin: 0x0 to 0x7
        def __init__(self, parent, pinid):
            ## holds reference to PycroHalInterface
            self._parent = parent
            ## holds pinid 0x2 (=D2) to 0xD (=D13)
            self._id = pinid
            ## holds last voltage read (float)
            self._voltage = None

        # --------------------
        ## the Pin's id (e.g. 7)
        #
        # @return  pin id
        @property
        def id(self):
            return self._id

        # --------------------
        ## returns the last voltage read (in volts)
        #
        # @return  the last voltage
        @property
        def voltage(self):
            return self._voltage

        # --------------------
        ## read the ADC pin.
        # up to caller to handler response
        #
        # @return None
        def read(self):
            self._parent.adc_read(self._id)

        # --------------------
        ## read the pin's ADC value, waits for response and save voltage
        #
        # @return None
        def read_voltage(self):
            self._parent.adc_read(self._id)
            rsp = self._parent.recv()
            self._voltage = self._parent.adc_to_voltage(rsp)

        # --------------------
        ## return human readable pin ID e.g. "A7".
        #
        # @return the pin id as a string.
        def __repr__(self):
            return f'A{self._id}'
