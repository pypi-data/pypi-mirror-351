"""Set of specific exceptions for the GA4GH Gateway."""


class SnapshotCreationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
