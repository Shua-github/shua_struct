from typing import Any, Callable
from abc import ABC, abstractmethod
import struct

class Field(ABC):
    @abstractmethod
    def get_length(self, context: dict | None = None) -> int: ...

    @classmethod
    @abstractmethod
    def parse(cls, data: bytes, context: dict | None = None) -> Any: ...

    @abstractmethod
    def build(self, value: Any = None, context: dict | None = None) -> bytes: ...

class IntField(Field, int):
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
class BytesField(Field, bytes):
    def __new__(cls, value: bytes | None = None, length: int | Callable[[dict], int] | None = None):
        if value is None:
            value = b''
        obj = super().__new__(cls, value)
        obj._length = length
        return obj

    def get_length(self, context: dict | None = None) -> int:
        if self._length is None:
            return len(self)
        elif callable(self._length):
            return self._length(context or {})
        else:
            return self._length

    def build(self, context=None) -> bytes:
        length = self.get_length(context)
        return self[:length]
    
    @classmethod
    def parse(cls, data: bytes, context: dict | None = None, length: int | Callable[[dict], int] | None = None) -> 'BytesField':
        if length is None:
            length = len(data)
        if callable(length):
            length = length(context or {})
        return cls(data[:length], length=length)

    def __repr__(self):
        return f"BytesField({bytes(self)!r}, length={self._length})"

    @property
    def value(self):
        return bytes(self)

__all__ = [
    "Field", "IntField",
    "Int8", "UInt8",
    "Int16", "UInt16",
    "Int32", "UInt32",
    "Int64", "UInt64",
    "BytesField"
]
