import pytest
import struct
import uuid
from protocol.packet_reading import RecMessage, RespMessage, FileProcessor, process_init, process_header, process_eof, handle_packet


# Helper function to create a sample packet
def create_packet(message_type, data):
    # Prepend message type
    return struct.pack(">B", message_type.value) + data


# Test `process_init` function
def test_process_init_valid():
    # Create a valid INIT packet with version 1
    transaction_id = 12345
    file_size = 2048
    checksum = 0x12345678
    file_uuid = uuid.uuid4()
    packet = struct.pack(">B B H I I 16s", RecMessage.INIT_PACKET.value, 1, transaction_id, file_size, checksum, file_uuid.bytes)

    # Call the process_init function
    transaction_id, fw = process_init(packet)

    # Assertions
    assert transaction_id == 12345
    assert fw.file_size == file_size
    assert fw.checksum == checksum
    assert fw.uuid == file_uuid


def test_process_init_invalid_version():
    # Create an invalid INIT packet with version 2
    packet = struct.pack(">B B H I I 16s", RecMessage.INIT_PACKET.value, 2, 12345, 2048, 0x12345678, uuid.uuid4().bytes)

    # Call the process_init function and expect a ValueError (due to invalid version)
    with pytest.raises(ValueError):
        process_init(packet)


# Test `process_header` function
def test_process_header():
    packet_number = 1
    payload_size = 1024
    checksum = 0x87654321
    payload_data = b"X" * payload_size  # Simulating payload data
    packet = struct.pack(">B H H I I", RecMessage.FOLLOW_UP_PACKET.value, 12345, packet_number, payload_size, checksum) + payload_data

    transaction_id, packet_number, payload_size, checksum, payload_data_out = process_header(packet)

    # Assertions
    assert transaction_id == 12345
    assert packet_number == 1
    assert payload_size == 1024
    assert checksum == 0x87654321
    assert payload_data_out == payload_data


# Test `process_eof` function
def test_process_eof():
    total_packets = 10
    packet = struct.pack(">B H H", RecMessage.END_PACKET.value, 12345, total_packets)

    transaction_id, total_packet = process_eof(packet)

    # Assertions
    assert transaction_id == 12345
    assert total_packet == 10


# Test `FileProcessor` class process method
def test_file_writer_process():
    file_size = 2048
    checksum = 0x12345678
    file_uuid = uuid.uuid4()
    fw = FileProcessor(file_size, checksum, file_uuid)

    # Simulate a valid packet
    packet_number = 1
    payload_size = 1024
    checksum = 0x87654321
    payload_data = b"X" * payload_size
    fw.process(packet_number, payload_size, checksum, payload_data)

    # Check if the file was written correctly
    assert fw.bytes_written == payload_size
    assert fw.packet_received == [packet_number]
    assert fw.file[:payload_size] == payload_data  # Ensure the file was updated


# Test `FileProcessor` class eof method
def test_file_writer_eof_valid():
    file_size = 2048
    checksum = 0x12345678
    file_uuid = uuid.uuid4()
    fw = FileProcessor(file_size, checksum, file_uuid)

    # Simulate writing the full file with correct checksum
    fw.bytes_written = file_size
    fw.checksum = checksum
    fw.file = b"X" * file_size  # Simulate file content

    # Simulate an EOF packet with 2 total packets
    result, data = fw.eof(2)

    # Assertions
    assert result is True
    assert data is None


def test_file_writer_eof_invalid():
    file_size = 2048
    checksum = 0x12345678
    file_uuid = uuid.uuid4()
    fw = FileProcessor(file_size, checksum, file_uuid)

    # Simulate writing an incomplete file with incorrect checksum
    fw.bytes_written = 1024  # Incomplete file
    fw.checksum = checksum
    fw.file = b"X" * 1024  # Simulate incomplete file content

    # Simulate an EOF packet with 2 total packets
    result, data = fw.eof(2)

    # Assertions
    assert result is False
    assert data is not None  # Missing packets should be reported
    assert data[:1] == b'\x02'  # Error message type
    assert len(data[1:]) == 2  # Should contain information about missing packets


# Test `handle_packet` function (integration test for the entire flow)
@pytest.fixture
def processes():
    return {}


def test_handle_packet_init(processes):
    # Simulate receiving an INIT packet
    transaction_id = 12345
    file_size = 2048
    checksum = 0x12345678
    file_uuid = uuid.uuid4()
    packet = struct.pack(">B B H I I 16s", RecMessage.INIT_PACKET.value, 1, transaction_id, file_size, checksum, file_uuid.bytes)

    handle_packet(processes, packet)

    # Assertions: Ensure the process is added to processes dictionary
    assert transaction_id in processes
    fw = processes[transaction_id]
    assert fw.file_size == file_size
    assert fw.checksum == checksum
    assert fw.uuid == file_uuid


def test_handle_packet_follow_up(processes):
    # Simulate receiving a FOLLOW_UP_PACKET
    transaction_id = 12345
    packet_number = 1
    payload_size = 1024
    checksum = 0x87654321
    payload_data = b"X" * payload_size
    packet = struct.pack(">B H H I I", RecMessage.FOLLOW_UP_PACKET.value, transaction_id, packet_number, payload_size, checksum) + payload_data

    # Simulate that the file writer is initialized
    processes[transaction_id] = FileProcessor(2048, 0x12345678, uuid.uuid4())

    handle_packet(processes, packet)

    # Assertions: Ensure that the data was processed
    fw = processes[transaction_id]
    assert fw.bytes_written == payload_size
    assert fw.packet_received == [packet_number]


def test_handle_packet_end(processes):
    # Simulate receiving an END_PACKET
    transaction_id = 12345
    total_packets = 2
    packet = struct.pack(">B H H", RecMessage.END_PACKET.value, transaction_id, total_packets)

    # Simulate that the file writer is initialized
    processes[transaction_id] = FileProcessor(2048, 0x12345678, uuid.uuid4())

    result, data = handle_packet(processes, packet)

    # Assertions: Ensure that the file writer was processed correctly
    assert result is True
    assert data is None

