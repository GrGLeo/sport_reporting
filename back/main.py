import threading
import time
from udp_server import udp_server
from file_watcher import file_watcher


if __name__ == "__main__":
    watch_directory = "/app/fit_file/"

    udp_thread = threading.Thread(target=udp_server, daemon=True)
    file_thread = threading.Thread(target=file_watcher, args=(watch_directory,), daemon=True)

    udp_thread.start()
    file_thread.start()

    while True:
        time.sleep(1)
