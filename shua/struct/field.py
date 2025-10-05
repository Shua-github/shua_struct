from typing import Any, Protocol, runtime_checkable
import struct

@runtime_checkable
class FieldProtocol(Protocol):
    def get_length(self, context: dict | None = None) -> int: ...
    def parse(self, data: bytes, context: dict | None = None) -> Any: ...
    def build(self, value: Any = None, context: dict | None = None) -> bytes: ...

class IntField(int):
    fmt: str
    size: int

    def __new__(cls, value=0):
        return super().__new__(cls, value)

    def build(self, context=None) -> bytes:
        return struct.pack(self.fmt, int(self))

    @classmethod
    def parse(cls, data: bytes, context=None):
        value = struct.unpack(cls.fmt, data[:cls.size])[0]
        return cls(value)

    def get_length(self, context=None) -> int:
        return self.size

# -----------------------------
class Int8(IntField):
    fmt = 'b'
    size = struct.calcsize(fmt)

class UInt8(IntField):
    fmt = 'B'
    size = struct.calcsize(fmt)
# -----------------------------
class Int16(IntField):
    fmt = '>h'
    size = struct.calcsize(fmt)

class UInt16(IntField):
    fmt = '>H'
    size = struct.calcsize(fmt)
# -----------------------------
class Int32(IntField):
    fmt = '>i'
    size = struct.calcsize(fmt)

class UInt32(IntField):
    fmt = '>I'
    size = struct.calcsize(fmt)
# -----------------------------
class Int64(IntField):
    fmt = '>q'
    size = struct.calcsize(fmt)

class UInt64(IntField):
    fmt = '>Q'
    size = struct.calcsize(fmt)

# -----------------------------
class BytesField(bytes):
    def __new__(cls, value: bytes | None = None, length: int | None = None):
        if value is None:
            value = b''
        obj = super().__new__(cls, value)
        obj._length = length
        return obj

    def get_length(self, context=None) -> int:
        if callable(self._length):
            return self._length(context or {})
        return self._length or len(self)

    def build(self, context=None) -> bytes:
        length = self.get_length(context)
        return self[:length]

    @classmethod
    def parse(cls, data: bytes, context=None, length=None):
        if length is None and context is not None:
            length = getattr(cls, '_length', None)
            if callable(length):
                length = length(context)
        length = length or len(data)
        return cls(data[:length], length=length)

    def __repr__(self):
        return f"BytesField({bytes(self)!r}, length={self._length})"

    @property
    def value(self):
        return bytes(self)

__all__ = [
    "FieldProtocol", "IntField",
    "Int8", "UInt8",
    "Int16", "UInt16",
    "Int32", "UInt32",
    "Int64", "UInt64",
    "BytesField"
]
