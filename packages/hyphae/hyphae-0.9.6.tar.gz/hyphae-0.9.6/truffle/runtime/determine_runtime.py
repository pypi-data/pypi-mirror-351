from enum import Enum
import os

class RuntimeType(Enum):
    DEV = 0,
    CLIENT = 1,
    TRUFFLE = 2

def determine_runtime() -> RuntimeType:
    
    rt_envvar = os.getenv("TRUFFLE_RUNTIME")

    if rt_envvar == "CLIENT": return RuntimeType.CLIENT
    elif rt_envvar == "DEV": return RuntimeType.DEV
    elif rt_envvar == "TRUFFLE": return RuntimeType.TRUFFLE
    else: return RuntimeType.CLIENT

