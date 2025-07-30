from enum import Enum
from pathlib import Path
import os
import platform
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class FileHandleMode(Enum):
    Traditional = 0
    Modern = 1

class FullPathBuilder:
    def __init__(self, spliter: str = os.path.sep, pathfilename: str = ''):
        self.__pathfilename = pathfilename
        self.__spliter = spliter
        self.__platform = platform.system().lower()

    def build(self) -> str:
        if not self.__pathfilename or not isinstance(self.__pathfilename, str):
            raise ValueError("Invalid pathfilename supplied.")

        ds = self.__pathfilename.split(self.__spliter)
        fullpath = Path.home()

        for d in ds:
            if not d == '~':
                fullpath = fullpath / d
        return str(fullpath)

class FileHandler:
    def __init__(self, handle: FileHandleMode = FileHandleMode.Modern):
        self.__handle = handle
        self.__content: str = ''

    @property
    def handlemode(self) -> FileHandleMode:
        return self.__handle

    @handlemode.setter
    def handlemode(self, mode: FileHandleMode):
        self.switchmode(mode)

    def switchmode(self, mode: FileHandleMode):
        self.__handle = mode

    def reset(self):
        self.__content = ''

    def __read_file_traditional(self, pathfilename: str):
        path = os.path.expanduser(pathfilename)
        logging.info(f"Reading (traditional) from file: {path}")
        with open(path, 'r', encoding='utf-8') as file:
            self.__content = file.read()

    def __write_file_traditional(self, pathfilename: str, content: str):
        path = os.path.expanduser(pathfilename)
        logging.info(f"Writing (traditional) to file: {path}")
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

    def __append_file_traditional(self, pathfilename: str, content: str):
        path = os.path.expanduser(pathfilename)
        logging.info(f"Appending (traditional) to file: {path}")
        with open(path, 'a', encoding='utf-8') as file:
            file.write(content)

    def __read_file_modern(self, pathfilename: str):
        path = FullPathBuilder('/', pathfilename).build()
        logging.info(f"Reading (modern) from file: {path}")
        with open(path, 'r', encoding='utf-8') as file:
            self.__content = file.read()

    def __write_file_modern(self, pathfilename: str, content: str):
        path = FullPathBuilder('/', pathfilename).build()
        logging.info(f"Writing (modern) to file: {path}")
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

    def __append_file_modern(self, pathfilename: str, content: str):
        path = FullPathBuilder('/', pathfilename).build()
        logging.info(f"Appending (modern) to file: {path}")
        with open(path, 'a', encoding='utf-8') as file:
            file.write(content)

    def read(self, pathfilename: str) -> str:
        if self.__handle == FileHandleMode.Traditional:
            self.__read_file_traditional(pathfilename)
        elif self.__handle == FileHandleMode.Modern:
            self.__read_file_modern(pathfilename)
        else:
            raise ValueError("Invalid file handle mode!")
        return self.__content

    def write(self, pathfilename: str, content: str):
        if self.__handle == FileHandleMode.Traditional:
            self.__write_file_traditional(pathfilename, content)
        elif self.__handle == FileHandleMode.Modern:
            self.__write_file_modern(pathfilename, content)
        else:
            raise ValueError("Invalid file handle mode!")

    def append(self, pathfilename: str, content: str):
        if self.__handle == FileHandleMode.Traditional:
            self.__append_file_traditional(pathfilename, content)
        elif self.__handle == FileHandleMode.Modern:
            self.__append_file_modern(pathfilename, content)
        else:
            raise ValueError("Invalid file handle mode!")

    def exists(self, pathfilename: str) -> bool:
        path = os.path.expanduser(pathfilename) if self.__handle == FileHandleMode.Traditional                else FullPathBuilder('/', pathfilename).build()
        return os.path.exists(path)

    def delete(self, pathfilename: str):
        path = os.path.expanduser(pathfilename) if self.__handle == FileHandleMode.Traditional                else FullPathBuilder('/', pathfilename).build()
        try:
            os.remove(path)
            logging.info(f"Deleted file: {path}")
        except FileNotFoundError:
            logging.warning(f"File not found (delete skipped): {path}")
        except Exception as e:
            raise IOError(f"Error deleting file {path}: {e}")

    def get_content(self) -> str:
        return self.__content
