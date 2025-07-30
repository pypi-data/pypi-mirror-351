from io import BufferedReader, BytesIO
from struct import unpack
from time import gmtime, strftime
from enum import Enum


REFERENCE_TIME = 2082844800

class InvalidMessageTypeException(Exception):
    pass

class MessageType(Enum):
    VITAL_SIGNS = b'\x0a\x00\x00\x00'
    LMAX = b'\x0b\x00\x00\x00'
    LEQ = b'\x0c\x00\x00\x00'
    LMIN = b'\x0d\x00\x00\x00'
    LPEAK = b'\x0e\x00\x00\x00'
    SETTINGS = b'\x0f\x00\x00\x00'

class Model(Enum):
    NS4 = b'\x4e\x53\x34'
    VS4 = '\x56\x53\x34'

class FirmwareRevision(Enum):
    V_1_7 = b'\x17'

class Weighting(Enum):
    DBC = 0
    DBA = 1
    DBZ = 2

class Message:
    def __init__(self, message_bytes, message_type):
        message_bytes.seek(0)
        self.message_type = message_type
        self.model = Model(message_bytes.read(3))
        self.firmware = FirmwareRevision(message_bytes.read(1))

class VitalSignsMessage(Message):
    def __init__(self, message_bytes):
        Message.__init__(self, message_bytes, MessageType.VITAL_SIGNS)
        message_bytes.seek(8)
        [
            time,
            self.timestamp_error_seconds,
            self.battery_voltage,
            self.temperature,
            self.rssi
        ] = unpack('<Qifff', message_bytes.read(24))
        self.timestamp = gmtime(time - REFERENCE_TIME)

class RecordedDataMessage(Message):
    def __init__(self, message_bytes, message_type):
        Message.__init__(self, message_bytes, message_type)
        message_bytes.seek(8)
        [
            f_utc,
            interval,
            self.sampling_frequency,
            weighting,
            self.tau,
            n_values
        ] = unpack('<QHHHfI', message_bytes.read(22))
        self.timestamp = gmtime(((f_utc * 125) / 1000) - REFERENCE_TIME)
        self.weighting = Weighting(weighting)
        self.values = list(unpack(
            '<'+('h'*n_values),
            message_bytes.read(2*n_values)
        ))
        self.sampling_interval_ms = interval * 125

class MessageParser:
    @staticmethod
    def parse(message_bytes):
        reader = BufferedReader(BytesIO(message_bytes))

        reader.seek(4)
        try:
            msgType = MessageType(reader.read(4))
        except:
            raise InvalidMessageTypeException()     

        if msgType is MessageType.VITAL_SIGNS:
            msg = VitalSignsMessage(reader)
        elif msgType is MessageType.SETTINGS:
            pass
        else:
            msg = RecordedDataMessage(reader, msgType)

        return msg
