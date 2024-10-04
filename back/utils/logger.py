import logging


class ConsoleLogger:
    __instances = None

    def __new__(cls, class_name):
        if cls.__instances is None:
            cls.__instances = super(ConsoleLogger, cls).__new__(cls)
            cls.__instances.__init__(class_name)
        return cls.__instances

    def __init__(self, class_name):
        self.logger = logging.getLogger(class_name)
        self.logger.setLevel(logging.INFO)  # Set default log level to INFO

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def critical(self, message):
        self.logger.critical(message)
