__all__ = ["SECTOR_SIZE", "Region", "Chunk", "CompressionTypes"]

import os
import gzip
import zlib
import re
from enum import Enum
from io import BytesIO
from typing import Optional, BinaryIO

from nbt_helper.file import JE_Uncompressed
from nbt_helper.tags import (
    BinaryHandler,
    ByteOrder,
    TagCompound,
)

SECTOR_SIZE = 4096
INT_SIZE = 4
MCA_FILE_PATTERN = re.compile(r"r\.-?\d+\.-?\d+\.mca")


class CompressionTypes(Enum):
    UNCOMPRESSED = 0
    GZIP_COMPRESSED = 1
    ZLIB_COMPRESSED = 2


def cords_from_location(location: int) -> tuple[int, int]:
    z = location >> 5
    x = location & 31
    return x, z


def location_from_cords(x: int, z: int) -> int:
    return x + (z << 5)


class Chunk:
    def __init__(
        self,
        x: int = 0,
        z: int = 0,
        timestamp: int = 0,
        compression: int = 0,
        data: Optional[TagCompound] = None,
    ) -> None:
        self._binary_handler = BinaryHandler(ByteOrder.BIG)
        self.x, self.z = x, z
        self.compression = compression
        self.timestamp = timestamp

        if data is None:
            data = TagCompound(self._binary_handler)
        self.data = data
        self.data.binary_handler = self._binary_handler

    def read_chunk(self, index: int, buffer: BinaryIO) -> None:
        self.x, self.z = cords_from_location(index)
        self._seek_to_location_table(buffer)
        location = self._binary_handler.read_int(buffer, signed=False)
        if location == 0:
            return

        offset = location >> 8

        buffer.seek(offset * SECTOR_SIZE)
        self._read_body(buffer)

        self._seek_to_timestamp_table(buffer)
        self.timestamp = self._binary_handler.read_int(buffer, signed=False)

    def _read_body(self, buffer: BinaryIO) -> None:
        length = self._binary_handler.read_int(buffer, signed=False)
        self.compression = self._binary_handler.read_byte(buffer, signed=False)
        chunk_data = self._decompress_chunk(buffer.read(length))
        self.data = JE_Uncompressed.read(chunk_data)

    def write_chunk(self, buffer: BinaryIO, offset: int) -> int:
        chunk_data_pos = offset * SECTOR_SIZE
        buffer.seek(chunk_data_pos)
        self._write_body(buffer)
        length = buffer.tell() - chunk_data_pos
        occupied_sectors = length // SECTOR_SIZE + 1
        self._add_padding(buffer, length, occupied_sectors)

        location = (offset << 8) | (occupied_sectors & 0b11111111)

        self._seek_to_location_table(buffer)
        self._binary_handler.write_int(buffer, location, signed=False)

        self._seek_to_timestamp_table(buffer)
        self._binary_handler.write_int(buffer, self.timestamp, signed=False)
        return occupied_sectors

    def _seek_to_location_table(self, buffer: BinaryIO) -> None:
        index = location_from_cords(self.x, self.z)
        buffer.seek(index * INT_SIZE)

    def _seek_to_timestamp_table(self, buffer: BinaryIO) -> None:
        index = location_from_cords(self.x, self.z)
        buffer.seek(index * INT_SIZE + SECTOR_SIZE)

    def _add_padding(
        self, buffer: BinaryIO, length: int, occupied_sectors: int
    ) -> None:
        padding = abs(length - SECTOR_SIZE * occupied_sectors) - 1
        buffer.seek(padding, os.SEEK_CUR)
        buffer.write(b"\x00")

    def _write_body(self, buffer: BinaryIO) -> None:
        temp_buffer = BytesIO()
        JE_Uncompressed.write(self.data, temp_buffer)
        chunk_data = self._compress_chunk(temp_buffer.getvalue())

        self._binary_handler.write_int(buffer, len(chunk_data), signed=False)
        self._binary_handler.write_byte(buffer, self.compression, signed=False)
        buffer.write(chunk_data)

    def _decompress_chunk(self, chunk_data: bytes) -> BytesIO:
        try:
            compression_type = CompressionTypes(self.compression)
        except ValueError:
            raise ValueError(f"Undefined compression type {self.compression}")

        if compression_type == CompressionTypes.GZIP_COMPRESSED:
            data = gzip.decompress(chunk_data)
        elif compression_type == CompressionTypes.ZLIB_COMPRESSED:
            data = zlib.decompress(chunk_data)
        elif compression_type == CompressionTypes.UNCOMPRESSED:
            data = chunk_data

        return BytesIO(data)  # type: ignore

    def _compress_chunk(self, chunk_data: bytes) -> bytes:
        try:
            compression_type = CompressionTypes(self.compression)
        except ValueError:
            raise ValueError(f"Undefined compression type {self.compression}")

        compression_type = CompressionTypes(self.compression)
        if compression_type == CompressionTypes.GZIP_COMPRESSED:
            data = gzip.compress(chunk_data)
        elif compression_type == CompressionTypes.ZLIB_COMPRESSED:
            data = zlib.compress(chunk_data)
        elif compression_type == CompressionTypes.UNCOMPRESSED:
            data = chunk_data
        return data  # type: ignore

    def __repr__(self) -> str:
        return f"Chunk(x={self.x}, z={self.z}, compression={self.compression}, timestamp={self.timestamp}, data={self.data})"

    def is_empty(self) -> bool:
        return not self.data.value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Chunk):
            return False
        return all((self.data == other.data, self.x == other.x, self.z == other.z))


class Region:
    def __init__(self, x: int = 0, z: int = 0, filepath: Optional[str] = None) -> None:
        self._binary_handler = BinaryHandler(ByteOrder.BIG)
        self.chunks: list[Chunk] = []
        self.x, self.z = x, z
        if filepath:
            self.load_region_file(filepath)

    def load_region_file(self, filepath: str) -> None:
        if not MCA_FILE_PATTERN.match(os.path.basename(filepath)):
            raise ValueError(
                f"Wrong file type or incorrect name. Filepath = {filepath}"
            )

        file_size = os.path.getsize(filepath)
        if file_size < SECTOR_SIZE * 2:
            raise ValueError(f"File '{filepath}' is too small.")

        self.x, self.z = self.cords_from_filepath(filepath)

        with open(filepath, "rb") as file:
            for index in range(SECTOR_SIZE // INT_SIZE):
                chunk = Chunk()
                chunk.read_chunk(index, file)
                self.chunks.append(chunk)

    def cords_from_filepath(self, filepath: str) -> tuple[int, int]:
        filepath = os.path.basename(filepath)
        filepath = filepath.replace("r.", "").replace(".mca", "")
        x, z = map(int, filepath.split("."))
        return x, z

    def write_region_file(self, output_folder: str) -> None:
        filepath = os.path.join(output_folder, f"r.{self.x}.{self.z}.mca")
        with open(filepath, "wb") as file:
            self._init_tables(file)
            offset = 100
            for chunk in self.chunks:
                if chunk.is_empty():
                    continue
                offset += chunk.write_chunk(file, offset)

    def _init_tables(self, buffer: BinaryIO) -> None:
        buffer.seek(SECTOR_SIZE * 2 - 1)
        buffer.write(b"\x00")

    def __repr__(self) -> str:
        return f"Region(x={self.x}, z={self.z}): [{len(self.chunks)} chunks]"
