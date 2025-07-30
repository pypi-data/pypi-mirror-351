import pytest
from io import BytesIO
from ci_msg_parser import *
from time import strftime

def test_it_fails_on_invalid_message_type():
    message = bytes.fromhex('4e53341700000000f231c4e3000000000000000049b08540ac6ce341000074c2')
    with pytest.raises(InvalidMessageTypeException):
        MessageParser.parse(message)

def test_it_parses_vital_signs_messages():
    message = bytes.fromhex('4e5334170a000000f231c4e3000000000000000049b08540ac6ce341000074c2')
    parsed = MessageParser.parse(message)

    assert isinstance(parsed, VitalSignsMessage)
    assert parsed.model is Model.NS4
    assert parsed.firmware is FirmwareRevision.V_1_7
    assert strftime('%Y-%m-%dT%H:%M:%SZ', parsed.timestamp) == '2025-02-01T20:17:54Z'
    assert parsed.timestamp_error_seconds == 0
    assert parsed.battery_voltage == 4.177769184112549
    assert parsed.temperature == 28.428062438964844
    assert parsed.rssi == -61

def test_it_parses_lmax_messages():
    message = bytes.fromhex('4e5334170b00000010e8211e07000000080080bb01000000003e13000000c801bf01c401cc01c501cd01c601d401c601c501bd01bb01c101cb01cc01be01c601d401c801')
    parsed = MessageParser.parse(message)

    assert isinstance(parsed, RecordedDataMessage)
    assert parsed.message_type == MessageType.LMAX
    assert parsed.model is Model.NS4
    assert parsed.firmware is FirmwareRevision.V_1_7
    assert strftime('%Y-%m-%dT%H:%M:%SZ', parsed.timestamp) == '2025-02-01T21:05:06Z'
    assert parsed.weighting == Weighting.DBA
    assert parsed.tau == 0.125
    assert parsed.sampling_frequency == 48000
    assert parsed.sampling_interval_ms == 1000
    assert parsed.values == [456, 447, 452, 460, 453, 461, 454, 468, 454, 453, 445, 443, 449, 459, 460, 446, 454, 468, 456]
