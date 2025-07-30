# NBT helper
This package provides tools for reading and writing Minecraft data files. 

The current version supports reading and writing all NBT tags and also reading and writing region files(.mca).

## Features
Module uses BinaryHandle, a special class for reading and writing binary data. Because of that, byte order can be easily changed.

> [!NOTE]
> Java Edition(JE) tags are big-endian, but Bedrock Edition(BE) tags are little-endian

## License
This packaged was inspired by [NBT](https://github.com/twoolie/NBT) package.