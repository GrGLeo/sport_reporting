import threading
import time
from queue import Queue
from udp_server import udp_server
from file_watcher import file_receiver


if __name__ == "__main__":
    watch_directory = "/app/fit_file/"
    data_queue = Queue()

    udp_thread = threading.Thread(target=udp_server, args=(data_queue,), daemon=True)
    # file_thread = threading.Thread(target=file_receiver, args=(data_queue,), daemon=True)

    udp_thread.start()
    # file_thread.start()

    while True:
        time.sleep(1)
