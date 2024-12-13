import socket
import struct
import uuid
import zlib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set the server's IP and port
SERVER_IP = "0.0.0.0"  # Listen on all available interfaces
SERVER_PORT = 12345
INIT_PACKET = 1
FOLLOW_UP_PACKET = 2
END_PACKET = 3
PAYLOAD_SIZE = 1011

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the server address and port
sock.bind((SERVER_IP, SERVER_PORT))


def decode_packet(data):
    message = data[0]
    if message == INIT_PACKET:
        # Define the format string based on the InitPacket structure
        # MessageType (uint8), TransactionID (uint16), FileSize (uint32), Checksum (uint32), UUID (16 bytes)
        format_string = ">B H I I 16s"  # Big-endian format: 1 byte, 2 bytes, 4 bytes, 4 bytes, 16 bytes

        # Unpack the data using the format string
        unpacked_data = struct.unpack(format_string, data)

        # Extract each field from the unpacked data
        message_type = unpacked_data[0]
        transaction_id = unpacked_data[1]
        file_size = unpacked_data[2]
        checksum = unpacked_data[3]
        uuid_bytes = unpacked_data[4]

        # Convert the UUID bytes to a UUID object
        packet_uuid = uuid.UUID(bytes=uuid_bytes)

        # Return the decoded packet as a dictionary
        return {
            'MessageType': message_type,
            'TransactionID': transaction_id,
            'FileSize': file_size,
            'Checksum': checksum,
            'UUID': packet_uuid
        }
    elif message == FOLLOW_UP_PACKET:
        header_data = data[:13]  # First 12 bytes are the header
        payload_data = data[13:]  # Rest is the payload

        header_format = ">BHHII"  # >: big-endian, B: uint8, H: uint16, I: uint32
        message_type, transaction_id, packet_number, payload_size, checksum = struct.unpack(header_format, header_data)
        logging.info(f"Received Follow-up Packet - {packet_number}")
        compute_checksum = zlib.crc32(payload_data) & 0xffffffff
        logging.info(f"Expected checksum: {checksum} | Computed checksum: {computed_checksum}")
        if compute_checksum != checksum:
            logging.info("invalid checksum")
        return {
            "PacketNumber": packet_number,
            "Packet": payload_data,
            "PayloadSize": payload_size
        }
    elif message == END_PACKET:
        header_format = ">B H H"
        print(len(data))
        message_type, transaction_id, packet_number = struct.unpack(header_format, data)
        return {
            "MessageType": message_type,
            "TransactionID": transaction_id,
            "PacketNumbers": packet_number
        }


logging.info(f"Listening on UDP port {SERVER_PORT}...")

# Listen for incoming messages
n = 0
s = 0
received_packet = []
while True:
    data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes

    if data[0] == INIT_PACKET:
        packet = decode_packet(data)
        filesize = packet["FileSize"]
        expected_checksum = packet["Checksum"]
        file = bytearray(filesize)
        sock.sendto(bytes([0x01]), addr)

    elif data[0] == FOLLOW_UP_PACKET:
        n += 1
        packet = decode_packet(data)
        packet_number = packet["PacketNumber"]
        payload = packet["Packet"]
        # logging.info(f"Packet data: {list(payload)}")
        s += packet["PayloadSize"]
        start_index = packet_number * PAYLOAD_SIZE
        end_index = start_index + PAYLOAD_SIZE

        # Write payload to the correct location in the file
        file[start_index:end_index] = payload
        received_packet.append(packet["PacketNumber"])

    elif data[0] == END_PACKET:
        packet = decode_packet(data)
        logging.info("end packet receive")
        if s == filesize:
            logging.info("File is a-ok")
            sock.sendto(bytes([0x01]), addr)
        else:
            data_format = ">B H"
            message = [3]
            missed = set(range(1, packet["PacketNumbers"])) - set(received_packet)
            message.append(len(missed))
            logging.info(missed)
            logging.info("File is not a-ok")
            for miss in missed:
                message.append(miss)
                data_format += " H"
            data = struct.pack(data_format, *message)
            logging.info(data)
            sock.sendto(data, addr)

    computed_checksum = zlib.crc32(file)

    # Log the decoded packet
    logging.info(f"Expected checksum: {expected_checksum} | Computed checksum: {computed_checksum}")
    logging.info(f"packet received: {n} | total byte: {s} / {filesize}")
