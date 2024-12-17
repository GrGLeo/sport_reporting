import socket
import logging
from protocol.packet_reading import handle_packet

SERVER_IP = "0.0.0.0"  # Listen on all available interfaces
SERVER_PORT = 12345
BUFFER_SIZE = 1024 * 1000

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)

# Bind the socket to the server address and port
sock.bind((SERVER_IP, SERVER_PORT))
logging.info("Listening on port 12345")

processes = {}
while True:
    data, addr = sock.recvfrom(1024)
    resp = handle_packet(processes, data)
    if resp is not None:
        sock.sendto(resp, addr)
