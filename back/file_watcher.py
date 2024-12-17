import struct
import watchdog
import time
import logging
import pandas as pd
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from fitparse import FitFile
from back.utils.data_handler import get_data
from back.data.etl.running_feeder import RunningFeeder
from back.data.etl.cycling_feeder import CyclingFeeder


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class FileWatcher(FileSystemEventHandler):
    def on_created(self, event: watchdog.events.FileSystemEvent):
        if event.is_directory:
            return
        file_path = event.src_path
        self.process_file(file_path)

    def process_file(self, file_path):
        while True:
            try:
                with open(file_path, "rb") as f:
                    logging.info("hello")
                    user_id_bytes = f.read(16)
                    user_id = struct.upack(">16s", user_id_bytes)[0]
                    data = f.read()
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
                    break

            except IOError:
                time.sleep(0.5)


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
