import argparse
import sys
from truffle.common import get_logger

logger = get_logger()

class ColorArgParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def _print_message(self, message, file=None):  
        if file == sys.stderr:
            logger.error(message)
        else:
            logger.plain_info(message)