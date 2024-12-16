from enum import Enum
import struct
import uuid
from zlib import crc32
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Set the server's IP and port
SERVER_IP = "0.0.0.0"  # Listen on all available interfaces
SERVER_PORT = 12345
VERSION = 1
# Packet message
PAYLOAD_SIZE = 1011


class RecMessage(Enum):
    INIT_PACKET = 1
    FOLLOW_UP_PACKET = 2
    END_PACKET = 3


class RespMessage(Enum):
    OK = bytes([1])
    NOT_OK = bytes([2])
    VERSION_ERR = bytes([5])


class FileWriter:
    def __init__(self, file_size, checksum, uuid):
        self.done = False
        self.file_size = file_size
        self.checksum = checksum
        self.uuid = uuid
        self.file = bytearray(file_size)
        self.packet_received = []
        self.bytes_written = 0

    @classmethod
    def process_init(cls, packet):
        # MessageType (uint8), Version (uint8), TransactionID (uint16), FileSize (uint32), Checksum (uint32), UUID (16 bytes)
        # Big-endian format: 1 byte, 1 byte,2 bytes, 4 bytes, 4 bytes, 16 bytes
        format_string = ">B B H I I 16s"

        # Unpack the data using the format string
        _, version, transaction_id, file_size, checksum, uuid_bytes = struct.unpack(format_string, packet)

        if version != VERSION:
            # TODO: make a custom error
            raise ValueError

        packet_uuid = uuid.UUID(bytes=uuid_bytes)

        # Return the decoded packet as a dictionary
        return transaction_id, cls(file_size, checksum, packet_uuid)

    def process(self, packet):
        transaction_id, packet_number, payload_size, checksum, payload = self._process_header(packet)
        compute_checksum = crc32(payload) & 0xffffffff
        if compute_checksum != checksum:
            # file is corrupt, we do not add it to our received packet and we do not write it
            return
        start_index = (packet_number - 1) * PAYLOAD_SIZE
        end_index = start_index + PAYLOAD_SIZE

        # Write payload to the correct location in the file
        self.file[start_index:end_index] = payload
        self.packet_received.append(packet_number)
        self.bytes_written += payload_size

    def eof(self, total_packet):
        header_format = ">B H H"
        _, transaction_id, total_packet = struct.unpack(header_format, packet)
        # compute total file packet
        compute_checksum = crc32(self.file) & 0xffffffff
        if self.bytes_written == self.file_size and compute_checksum == self.checksum:
            # File received succesfully
            self.done = True
            return True, RespMessage.OK.value

        # WARN: should we send back the transactionID?
        # ErrorMessage (uint8), MissedPackets (uint16), ...PacketNumber (uint16)
        data_format = ">B H"
        message = [0x02]
        missed = set(range(1, total_packet)) - set(self.packet_received)
        message.append(len(missed))
        for miss in missed:
            message.append(miss)
            data_format += " H"
        data = struct.pack(data_format, *message)
        return False, data

    def _process_header(packet):
        header_data = packet[:13]  # First 12 bytes are the header
        payload_data = packet[13:]  # Rest is the payload

        # MessageType (uint8), TransactionID (uint16), PacketNumber (uint16), PayloadSize (uint32), Checksum (uint32)
        # Big-endian format: 1 byte, 2 bytes, 2 bytes, 4 bytes, 4 bytes
        header_format = ">B H H I I"
        _, transaction_id, packet_number, payload_size, checksum = struct.unpack(header_format, header_data)
        return transaction_id, packet_number, payload_size, checksum, payload_data

    def __str__(self):
        return f"Received: {(self.bytes_written/self.file_size) * 100}%"


def handle_packet(processes: dict, packet):
    message = packet[0]
    logging.info(RecMessage.INIT_PACKET.value)
    match message:
        case RecMessage.INIT_PACKET.value:
            try:
                transaction_id, fw = FileWriter.process_init(packet)
                processes[transaction_id] = fw
                return RespMessage.OK.value
            except ValueError:
                # We send back a version missmatched ack
                return RespMessage.VERSION_ERR.value
        case RecMessage.FOLLOW_UP_PACKET.value:
            transaction_id, packet_number, payload_size, checksum, payload_data = process_header(packet)
            fw = processes.get(transaction_id)
            fw.process(packet_number, payload_size, checksum, payload_data)
            return None
        case RecMessage.END_PACKET.value:
            transaction_id, total_packet = process_eof(packet)
            fw = processes.get(transaction_id)
            ok, data = fw.eof(total_packet)
            if not ok:
                # We send the num packet missing
                return data
            else:
                del processes[transaction_id]
                return RespMessage.OK.value


def process_eof(packet):
    # MessageType (uint8), TransactionID (uint16), TotalPackets(uint16)
    # Big-endian format: 1 byte, 2 bytes, 2 bytes
    header_format = ">B H H"
    _, transaction_id, total_packet = struct.unpack(header_format, packet)
    return transaction_id, total_packet
