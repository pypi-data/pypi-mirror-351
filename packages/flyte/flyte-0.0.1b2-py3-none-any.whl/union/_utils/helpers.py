import os
import string
import typing
from pathlib import Path


def load_proto_from_file(pb2_type, path):
    with open(path, "rb") as reader:
        out = pb2_type()
        out.ParseFromString(reader.read())
        return out


def write_proto_to_file(proto, path):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as writer:
        writer.write(proto.SerializeToString())


def str2bool(value: typing.Optional[str]) -> bool:
    """
    Convert a string to a boolean. This is useful for parsing environment variables.
    :param value: The string to convert to a boolean
    :return: the boolean value
    """
    if value is None:
        return False
    return value.lower() in ("true", "t", "1")


BASE62_ALPHABET = string.digits + string.ascii_letters  # 0-9 + A-Z + a-z (62 characters)


def base62_encode(byte_data: bytes) -> str:
    # Convert bytes to a big integer
    num = int.from_bytes(byte_data, byteorder="big")

    # Convert integer to base62 string
    if num == 0:
        return BASE62_ALPHABET[0]

    base62 = []
    while num:
        num, rem = divmod(num, 62)
        base62.append(BASE62_ALPHABET[rem])
    return "".join(reversed(base62))
