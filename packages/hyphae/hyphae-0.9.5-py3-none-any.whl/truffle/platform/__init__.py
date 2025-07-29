from . import sdk_pb2_grpc
from . import sdk_pb2
from truffle.runtime import HOST, RuntimeType
import os 

APP_SOCK = (
    os.getenv("TRUFFLE_APP_SOCKET")
    if os.getenv("TRUFFLE_APP_SOCKET") is not None
    else "unix:///tmp/truffle_app.sock"
)
SDK_SOCK = (
    os.getenv("TRUFFLE_SDK_SOCKET")
    if os.getenv("TRUFFLE_SDK_SOCKET") is not None
    else "unix:///tmp/truffle_sdk.sock"
)

SHARED_DIR = (
    os.getenv("TRUFFLE_SHARED_DIR")
    if os.getenv("TRUFFLE_SHARED_DIR") is not None
    else "/root/shared"  # container default 1.31.25
)

if HOST is RuntimeType.TRUFFLE:
    if not os.getenv("TRUFFLE_APP_SOCKET") or not os.getenv("TRUFFLE_SDK_SOCKET"):
        raise Exception("TRUFFLE_APP_SOCKET and TRUFFLE_SDK_SOCKET must be set when using Truffle SDK")
        