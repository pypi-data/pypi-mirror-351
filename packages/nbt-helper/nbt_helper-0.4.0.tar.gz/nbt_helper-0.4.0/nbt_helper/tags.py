__all__ = [
    "ByteOrder",
    "BinaryHandler",
    "BaseTag",
    "BaseNumTag",
    "BaseFloatTag",
    "TagByte",
    "TagShort",
    "TagInt",
    "TagLong",
    "TagFloat",
    "TagDouble",
    "TagString",
    "TagList",
    "TagCompound",
    "TagIntArray",
    "TagLongArray",
    "TagByteArray",
]


import struct
from enum import Enum
from abc import ABC, abstractmethod
from typing import BinaryIO, Any, BinaryIO, Sequence, Optional, TypeVar

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12

V = TypeVar("V", bound="Any")


class ByteOrder(Enum):
    LITTLE = "<"
    BIG = ">"


class BinaryHandler:
    def __init__(self, byte_order: ByteOrder = ByteOrder.BIG) -> None:
        self.change_byte_order(byte_order)

    def change_byte_order(self, new_order: ByteOrder) -> None:
        self._order = new_order.value
        self._byte = struct.Struct(f"{self._order}b")
        self._short = struct.Struct(f"{self._order}h")
        self._int = struct.Struct(f"{self._order}i")
        self._long = struct.Struct(f"{self._order}q")
        self._float = struct.Struct(f"{self._order}f")
        self._double = struct.Struct(f"{self._order}d")

        self._ubyte = struct.Struct(f"{self._order}B")
        self._ushort = struct.Struct(f"{self._order}H")
        self._uint = struct.Struct(f"{self._order}I")
        self._ulong = struct.Struct(f"{self._order}Q")

    def get_byte_order(self) -> ByteOrder:
        return ByteOrder(self._order)

    def read_byte(self, buffer: BinaryIO, signed: bool = True) -> int:
        unpacker = self._byte if signed else self._ubyte
        return unpacker.unpack(buffer.read(1))[0]

    def read_short(self, buffer: BinaryIO, signed: bool = True) -> int:
        unpacker = self._short if signed else self._ushort
        return unpacker.unpack(buffer.read(2))[0]

    def read_int(self, buffer: BinaryIO, signed: bool = True) -> int:
        unpacker = self._int if signed else self._uint
        return unpacker.unpack(buffer.read(4))[0]

    def read_long(self, buffer: BinaryIO, signed: bool = True) -> int:
        unpacker = self._long if signed else self._ulong
        return unpacker.unpack(buffer.read(8))[0]

    def read_float(self, buffer: BinaryIO) -> float:
        return self._float.unpack(buffer.read(4))[0]

    def read_double(self, buffer: BinaryIO) -> float:
        return self._double.unpack(buffer.read(8))[0]

    def read_int_array(self, buffer: BinaryIO, size: int) -> tuple[int]:
        fmt = struct.Struct(f"{self._order}{size}i")
        return fmt.unpack(buffer.read(fmt.size))

    def read_long_array(self, buffer: BinaryIO, size: int) -> tuple[int]:
        fmt = struct.Struct(f"{self._order}{size}q")
        return fmt.unpack(buffer.read(fmt.size))

    def write_byte(self, buffer: BinaryIO, value: int, signed: bool = True) -> None:
        packer = self._byte if signed else self._ubyte
        buffer.write(packer.pack(value))

    def write_short(self, buffer: BinaryIO, value: int, signed: bool = True) -> None:
        packer = self._short if signed else self._ushort
        buffer.write(packer.pack(value))

    def write_int(self, buffer: BinaryIO, value: int, signed: bool = True) -> None:
        packer = self._int if signed else self._uint
        buffer.write(packer.pack(value))

    def write_long(self, buffer: BinaryIO, value: int, signed: bool = True) -> None:
        packer = self._long if signed else self._ulong
        buffer.write(packer.pack(value))

    def write_float(self, buffer: BinaryIO, value: float) -> None:
        buffer.write(self._float.pack(value))

    def write_double(self, buffer: BinaryIO, value: float) -> None:
        buffer.write(self._double.pack(value))

    def write_int_array(self, buffer: BinaryIO, values: Sequence[int]) -> None:
        size = len(values)
        fmt = struct.Struct(f"{self._order}{size}i")
        buffer.write(fmt.pack(*values))

    def write_long_array(self, buffer: BinaryIO, values: Sequence[int]) -> None:
        size = len(values)
        fmt = struct.Struct(f"{self._order}{size}q")
        buffer.write(fmt.pack(*values))


class BaseTag(ABC):
    TAG_ID = TAG_END

    def __init__(
        self,
        binary_handler: BinaryHandler,
        name: str = "",
        value: Any = None,
        buffer: Optional[BinaryIO] = None,
    ) -> None:
        self.binary_handler = binary_handler
        self.name = name
        self.value = value
        if buffer:
            self.load_from_buffer(buffer)

    @abstractmethod
    def load_from_buffer(self, buffer: BinaryIO) -> None: ...

    @abstractmethod
    def write_to_buffer(self, buffer: BinaryIO) -> None: ...

    def get_byte_order(self) -> ByteOrder:
        return self.binary_handler.get_byte_order()

    def change_byte_order(self, new_byte_order: ByteOrder) -> None:
        self.binary_handler.change_byte_order(new_byte_order)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r}): {self.value}"

    def __eq__(self, other) -> bool:
        if issubclass(type(other), BaseTag):
            return all(
                (
                    self.TAG_ID == other.TAG_ID,
                    other.name == self.name,
                    other.value == self.value,
                )
            )
        return False


class BaseNumTag(BaseTag):
    def __init__(
        self,
        binary_handler: BinaryHandler,
        name: str = "",
        value: int = 0,
        buffer: Optional[BinaryIO] = None,
    ) -> None:
        super().__init__(binary_handler, name, value, buffer)

    def __eq__(self, other) -> bool:
        if isinstance(other, (int, float)):
            return self.value == other
        return super().__eq__(other)


class TagByte(BaseNumTag):
    TAG_ID = TAG_BYTE

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.value = self.binary_handler.read_byte(buffer)

    def write_to_buffer(self, buffer: BinaryIO) -> None:
        self.binary_handler.write_byte(buffer, self.value)


class TagShort(BaseNumTag):
    TAG_ID = TAG_SHORT

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.value = self.binary_handler.read_short(buffer)

    def write_to_buffer(self, buffer: BinaryIO) -> None:
        self.binary_handler.write_short(buffer, self.value)


class TagInt(BaseNumTag):
    TAG_ID = TAG_INT

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.value = self.binary_handler.read_int(buffer)

    def write_to_buffer(self, buffer: BinaryIO) -> None:
        self.binary_handler.write_int(buffer, self.value)


class TagLong(BaseNumTag):
    TAG_ID = TAG_LONG

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.value = self.binary_handler.read_long(buffer)

    def write_to_buffer(self, buffer: BinaryIO) -> None:
        self.binary_handler.write_long(buffer, self.value)


class BaseFloatTag(BaseTag):
    def __init__(
        self,
        binary_handler: BinaryHandler,
        name: str = "",
        value: float = 0,
        buffer: Optional[BinaryIO] = None,
    ) -> None:
        super().__init__(binary_handler, name, value, buffer)

    def __eq__(self, other) -> bool:
        if isinstance(other, (int, float)):
            return self.value == other
        return super().__eq__(other)


class TagFloat(BaseFloatTag):
    TAG_ID = TAG_FLOAT

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.value = self.binary_handler.read_float(buffer)

    def write_to_buffer(self, buffer: BinaryIO) -> None:
        self.binary_handler.write_float(buffer, self.value)


class TagDouble(BaseFloatTag):
    TAG_ID = TAG_DOUBLE

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.value = self.binary_handler.read_double(buffer)

    def write_to_buffer(self, buffer: BinaryIO) -> None:
        self.binary_handler.write_double(buffer, self.value)


class TagString(BaseTag):
    TAG_ID = TAG_STRING

    def __init__(
        self,
        binary_handler: BinaryHandler,
        name: str = "",
        value: str = "",
        buffer: Optional[BinaryIO] = None,
    ) -> None:
        super().__init__(binary_handler, name, value, buffer)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        length = self.binary_handler.read_short(buffer)
        data = buffer.read(length)
        if len(data) != length:
            raise ValueError(f"String length not equal: {length=}, {data=}.")
        self.value = data.decode("utf-8")

    def write_to_buffer(self, buffer: BinaryIO) -> None:
        data = self.value.encode("utf-8")
        self.binary_handler.write_short(buffer, len(data))
        buffer.write(data)


class TagList(BaseTag):
    TAG_ID = TAG_LIST

    def __init__(
        self,
        binary_handler: BinaryHandler,
        name: str = "",
        value: Optional[Sequence] = None,
        buffer: Optional[BinaryIO] = None,
        tag_id: int = TAG_END,
    ) -> None:
        self.tag_id = tag_id
        super().__init__(binary_handler, name, [], buffer)

        if value:
            self.value.extend(value)
            self.tag_id = value[0].TAG_ID

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.tag_id = self.binary_handler.read_byte(buffer)
        length = self.binary_handler.read_int(buffer)
        self.value = [
            TAGS_LIST[self.tag_id](self.binary_handler, buffer=buffer)
            for _ in range(length)
        ]

    def write_to_buffer(self, buffer: BinaryIO) -> None:
        if self.tag_id == TAG_END and self.value:
            self.tag_id = self.value[0].TAG_ID
        self.binary_handler.write_byte(buffer, self.tag_id)
        self.binary_handler.write_int(buffer, len(self.value))

        for tag in self.value:
            tag.write_to_buffer(buffer)

    def append(self, item: BaseTag) -> None:
        self.value.append(item)

    def __repr__(self) -> str:
        return f"TagList('{self.name}') [{len(self.value)}]"

    def __iter__(self):
        yield from self.value

    def __getitem__(self, index: int) -> Any:
        if not isinstance(index, int):
            raise ValueError("Index must be an integer.")

        return self.value[index]

    def __setitem__(self, index: int, item: Any) -> None:
        if not isinstance(index, int):
            raise ValueError("Index must be a string.")
        if not issubclass(type(item), BaseTag):
            raise ValueError("Value must be a subclass of BaseTag.")
        self.value[index] = item

    def __len__(self) -> int:
        return len(self.value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, TagList):
            return False
        return all(
            (
                self.tag_id == other.tag_id,
                self.name == other.name,
                self.value == other.value,
            )
        )


class TagCompound(BaseTag):
    TAG_ID = TAG_COMPOUND

    def __init__(
        self,
        binary_handler: BinaryHandler,
        name: str = "",
        value: Optional[Sequence] = None,
        buffer: Optional[BinaryIO] = None,
    ) -> None:
        super().__init__(binary_handler, name, [], buffer)
        if value:
            self.value.extend(value)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        while True:
            tag_type = self.binary_handler.read_byte(buffer)
            if tag_type == TAG_END:
                break
            name = TagString(self.binary_handler, buffer=buffer).value
            tag = TAGS_LIST[tag_type](self.binary_handler, name=name, buffer=buffer)
            self.value.append(tag)

    def write_to_buffer(self, buffer: BinaryIO) -> None:
        for tag in self.value:
            self.binary_handler.write_byte(buffer, tag.TAG_ID)
            TagString(
                self.binary_handler,
                value=tag.name,
            ).write_to_buffer(buffer)

            tag.write_to_buffer(buffer)

        self.binary_handler.write_byte(buffer, TAG_END)

    def get_tag(self, key: str, default: Optional[V] = None) -> Optional[V]:
        if not isinstance(key, str):
            raise ValueError("Key must be a string.")
        result = default
        if key in self:
            result = self[key]
        return result

    def get_value(self, key: str, default: Optional[V] = None) -> Optional[V]:
        if not isinstance(key, str):
            raise ValueError("Key must be a string.")
        result = default
        if key in self:
            result = self[key].value
        return result

    def pop(self, key: str) -> Any:
        if not isinstance(key, str):
            raise ValueError("Key must be a string.")
        result = self.get_value(key)
        del self[key]

        return result

    def append(self, item: BaseTag) -> None:
        self.value.append(item)

    def __delitem__(self, key: str) -> None:
        if not isinstance(key, str):
            raise ValueError("Key must be a string.")
        res = [tag for tag in self.value if tag.name != key]
        self.value = res

    def __iter__(self):
        yield from self.value

    def __getitem__(self, key: str) -> Any:
        if not isinstance(key, str):
            raise ValueError("Key must be a string.")
        for tag in self.value:
            if tag.name == key:
                return tag
        raise KeyError(f"'{key}' does not exist.")

    def __setitem__(self, key: str, item: Any) -> None:
        if not isinstance(key, str):
            raise ValueError("Key must be a string.")
        if not issubclass(type(item), BaseTag):
            raise ValueError("Value must be a subclass of BaseTag.")
        item.name = key
        self.value.append(item)

    def __contains__(self, key: str) -> bool:
        if not isinstance(key, str):
            raise ValueError("Key must be a string.")
        return any(key == tag.name for tag in self.value)

    def __len__(self) -> int:
        return len(self.value)


class TagIntArray(BaseTag):
    TAG_ID = TAG_INT_ARRAY

    def __init__(
        self,
        binary_handler: BinaryHandler,
        name: str = "",
        value: Optional[Sequence] = None,
        buffer: Optional[BinaryIO] = None,
    ) -> None:
        super().__init__(binary_handler, name, [], buffer)
        if value:
            self.value.extend(value)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        length = self.binary_handler.read_int(buffer)
        self.value = list(self.binary_handler.read_int_array(buffer, length))

    def write_to_buffer(self, buffer: BinaryIO) -> None:
        lenght = len(self.value)
        self.binary_handler.write_int(buffer, lenght)
        self.binary_handler.write_int_array(buffer, self.value)

    def __iter__(self):
        yield from self.value


class TagLongArray(BaseTag):
    TAG_ID = TAG_LONG_ARRAY

    def __init__(
        self,
        binary_handler: BinaryHandler,
        name: str = "",
        value: Optional[Sequence] = None,
        buffer: Optional[BinaryIO] = None,
    ) -> None:
        super().__init__(binary_handler, name, [], buffer)
        if value:
            self.value.extend(value)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        length = self.binary_handler.read_int(buffer)
        self.value = list(self.binary_handler.read_long_array(buffer, length))

    def write_to_buffer(self, buffer: BinaryIO) -> None:
        lenght = len(self.value)
        self.binary_handler.write_int(buffer, lenght)
        self.binary_handler.write_long_array(buffer, self.value)

    def __iter__(self):
        yield from self.value


class TagByteArray(BaseTag):
    TAG_ID = TAG_BYTE_ARRAY

    def __init__(
        self,
        binary_handler: BinaryHandler,
        name: str = "",
        value: Optional[bytearray] = None,
        buffer: Optional[BinaryIO] = None,
    ) -> None:
        super().__init__(binary_handler, name, value or bytearray(), buffer)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        length = self.binary_handler.read_int(buffer)
        self.value = bytearray(buffer.read(length))

    def write_to_buffer(self, buffer: BinaryIO) -> None:
        lenght = len(self.value)
        self.binary_handler.write_int(buffer, lenght)
        buffer.write(self.value)

    def __iter__(self):
        yield from self.value


TAGS_LIST = {
    TAG_BYTE: TagByte,
    TAG_SHORT: TagShort,
    TAG_INT: TagInt,
    TAG_LONG: TagLong,
    TAG_FLOAT: TagFloat,
    TAG_DOUBLE: TagDouble,
    TAG_STRING: TagString,
    TAG_LIST: TagList,
    TAG_COMPOUND: TagCompound,
    TAG_INT_ARRAY: TagIntArray,
    TAG_LONG_ARRAY: TagLongArray,
    TAG_BYTE_ARRAY: TagByteArray,
}
