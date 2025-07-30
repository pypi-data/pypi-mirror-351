import logging
from maskteer import Maskteer

class MaskteerHandler(logging.Handler):
    def __init__(self, config_file=None):
        super().__init__()
        self.maskteer = Maskteer(config_file)

    def emit(self, record):
        log_entry = self.format(record)
        masked_log_entry = self.maskteer.mask_text(log_entry)
        super().emit(record, masked_log_entry)
