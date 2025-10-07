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
        obj_kwargs = {}
        
        for name, (field_type, default) in cls._fields_info.items():
            if default is not None:
                field_length = default.get_length(ctx)
            else:
                temp_instance = field_type()
                field_length = temp_instance.get_length(ctx)
            
            if field_length > len(data):
                raise ValueError(f"Insufficient data for field '{name}': expected {field_length}, got {len(data)}")
            
            field_data = data[:field_length]
            value = field_type.parse(field_data, ctx)
            
            data = data[field_length:]
            ctx[name] = value
            obj_kwargs[name] = value
        
        return cls(**obj_kwargs)

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