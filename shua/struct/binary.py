from typing import Type, TypeVar, Any
from shua.struct.field import Field
from abc import ABCMeta

class BinaryMeta(ABCMeta):
    def __new__(cls, name, bases, namespace):
        fields = {}
        annotations = namespace.get('__annotations__', {})
        
        for field_name, field_type in annotations.items():
            if not isinstance(field_type, type):
                raise TypeError(f"Field '{field_name}' annotation must be a class, got {type(field_type)}")

            if not issubclass(field_type, Field):
                raise TypeError(f"Field '{field_name}' type must be a subclass of Field")

            default = namespace.get(field_name, None)
            fields[field_name] = (field_type, default)
        
        namespace['_fields_info'] = fields
        return super().__new__(cls, name, bases, namespace)

T = TypeVar('T', bound='BinaryStruct')

class BinaryStruct(Field, metaclass=BinaryMeta):
    _fields_info = None  # type: dict[str, tuple[Type[Field], Any]]
    def __init__(self, **kwargs):
        for field_name, (field_type, default) in self._fields_info.items():
            value = kwargs.get(field_name, default)
            
            if value is None:
                if default is not None:
                    value = default
                else:
                    value = field_type()
            elif not isinstance(value, field_type):
                value = field_type(value)
            
            setattr(self, field_name, value)

    @classmethod
    def parse(cls: Type[T], data: bytes, context: dict | None = None) -> T:
        if context is None:
            context = {}
        ctx = context.copy()
        offset = 0
        obj_kwargs = {}
        
        for name, (field_type, default) in cls._fields_info.items():
            field_length = cls._get_field_length(name, field_type, default, ctx, data, offset)
            field_data = data[offset:offset + field_length]
            if len(field_data) < field_length:
                raise ValueError(f"Insufficient data for field '{name}' at offset {offset}: expected {field_length}, got {len(field_data)}")
            
            value = field_type.parse(data, context)
            
            offset += field_length
            ctx[name] = value
            obj_kwargs[name] = value
        
        return cls(**obj_kwargs)

    @classmethod
    def _get_field_length(cls, name: str, field_type: Type[Field], default: Any, context: dict, data: bytes, offset: int) -> int:
        if default is not None:
            return default.get_length(context)
        else:
            temp_instance = field_type()
            return temp_instance.get_length(context)

    def get_length(self, context: dict | None = None) -> int:
        if context is None:
            context = {}
        total_length = 0
        ctx = context.copy()
        
        for name, (field_type, default) in self._fields_info.items():
            value = getattr(self, name)
            field_length = value.get_length(ctx)
            total_length += field_length
            ctx[name] = value
            
        return total_length

    def build(self, context: dict | None = None) -> bytes:
        if context is None:
            context = {}
        result = []
        ctx = context.copy()
        
        for name, (field_type, default) in self._fields_info.items():
            value = getattr(self, name)
            built_data = value.build(ctx)
            result.append(built_data)
            ctx[name] = value
            
        return b''.join(result)

    def __repr__(self):
        fields = []
        for name, (field_type, default) in self._fields_info.items():
            value = getattr(self, name)
            fields.append(f"{name}={value!r}")
        return f"{self.__class__.__name__}({', '.join(fields)})"

    def __getitem__(self, key):
        return getattr(self, key)

__all__ = ["BinaryStruct"]