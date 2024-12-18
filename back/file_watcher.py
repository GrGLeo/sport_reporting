import struct
import watchdog
import time
import logging
import pandas as pd
from uuid import UUID
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from fitparse import FitFile
from utils.data_handler import get_data
from data.etl.running_feeder import RunningFeeder
from data.etl.cycling_feeder import CyclingFeeder


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class FileWatcher(FileSystemEventHandler):
    def on_moved(self, event: watchdog.events.FileSystemEvent):
        logging.info("Called on modified")
        if event.is_directory:
            return
        logging.info(type(event))
        file_path = event.dest_path
        logging.info(file_path)
        if file_path.endswith(".fit"):
            logging.info(".fit found")
            self.process_file(file_path)

    def process_file(self):
        pass


def process_file(fit_file):
    logging.info("hello")
    user_id_bytes = fit_file[:16]
    data = fit_file[16:]
    user_id_unpack = struct.unpack(">16s", user_id_bytes)[0]
    user_id = UUID(bytes=user_id_unpack)
    fitfile = FitFile(data)
    records = get_data(fitfile, 'record')
    laps = get_data(fitfile, 'lap')
    activity = get_data(fitfile, 'session')[0]['sport']
    activity_id = int(records[0]["timestamp"].timestamp())

    wkt = {
            f"record_{activity}": pd.DataFrame(records),
            f"lap_{activity}": pd.DataFrame(laps)
            }

    if activity == "running":
        feeder = RunningFeeder(wkt, activity_id, user_id)
        feeder.compute()
    elif activity == "cycling":
        feeder = CyclingFeeder(wkt, activity_id, user_id)
        feeder.compute()
    if feeder.complete:
        return


def file_receiver(data_queue):
    while True:
        if not data_queue.empty():
            fit_file = data_queue.get(block=False)
            process_file(fit_file)


def file_watcher(watch_directory):
    event_handler = FileWatcher()
    observer = Observer()
    observer.schedule(event_handler, watch_directory, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
