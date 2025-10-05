from typing import Type, TypeVar
from shua.struct.field import FieldProtocol

class BinaryMeta(type):
    def __new__(cls, name, bases, namespace):
        fields = {}
        annotations = namespace.get('__annotations__', {})
        
        for k, typ in annotations.items():
            default = namespace.get(k, None)
            if default is None:
                default = typ()
            fields[k] = (typ, default)
        
        namespace['_fields'] = fields
        return super().__new__(cls, name, bases, namespace)

T = TypeVar('T', bound='BinaryStruct')

class BinaryStruct(metaclass=BinaryMeta):
    def __init__(self, **kwargs):
        for k, (typ, default) in self._fields.items():
            value = kwargs.get(k, default)
            
            if default is not None:   
                if not isinstance(value,FieldProtocol):
                    try:
                        value = default.__class__(value)
                    except (TypeError, ValueError):
                        pass
            
            setattr(self, k, value)

    @classmethod
    def parse(cls: Type[T], data: bytes) -> T:
        ctx = {}
        offset = 0
        obj_kwargs = {}
        
        for name, (typ, default) in cls._fields.items():
            if hasattr(default, 'get_length'):
                field_length = default.get_length(ctx)
            elif hasattr(default, 'size'):
                field_length = default.size
            else:
                field_length = len(data) - offset
            
            field_length = int(field_length)
            
            field_data = data[offset:offset + field_length]
            
            if hasattr(default, 'parse'):
                value = default.parse(field_data, ctx)
            else:
                value = field_data
                if hasattr(typ, 'parse'):
                    value = typ.parse(field_data)
            
            offset += field_length
            ctx[name] = value
            obj_kwargs[name] = value
        
        return cls(**obj_kwargs)

    def build(self) -> bytes:
        result = []
        ctx = self.__dict__.copy()
        
        for name, (typ, default) in self._fields.items():
            val = getattr(self, name)
            
            if hasattr(val, 'build'):
                result.append(val.build(ctx))
            elif hasattr(default, 'build'):
                result.append(default.build(val, ctx))
            elif isinstance(val, bytes):
                result.append(val)
            else:
                try:
                    result.append(bytes(val))
                except Exception:
                    raise TypeError(f"Cannot build field {name}: {val}")
        
        return b''.join(result)

    def __repr__(self):
        fields = []
        for name, (typ, default) in self._fields.items():
            value = getattr(self, name)
            fields.append(f"{name}={value!r}")
        return f"{self.__class__.__name__}({', '.join(fields)})"

__all__ = ["BinaryStruct"]