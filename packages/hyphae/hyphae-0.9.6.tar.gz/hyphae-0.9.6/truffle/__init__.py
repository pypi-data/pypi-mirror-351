from typing import List, Dict, Any

from .runtime import Runtime, tool, args, group, app, flags, HOST
from .common import get_logger



from .api import *
from .types import *

import logging 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = get_logger()

env : api.TGlobals = api.TGlobals()

def run(class_instance: Any) -> Any:
    logger.info(f"Building and running Truffle app: {class_instance.__class__.__name__}")
    rt = Runtime()()
    return rt.build(class_instance)