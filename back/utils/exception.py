class UserTaken(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class EmailTaken(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class UnknownUser(Exception):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Invalid username"


class FailedAttempt(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class UserLocked(Exception):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "User is locked"
