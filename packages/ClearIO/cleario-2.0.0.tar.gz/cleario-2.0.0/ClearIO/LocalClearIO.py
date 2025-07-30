from enum import Enum
from pathlib import Path
import platform
import re
from .IClearIO import IClearIO
from .TypedPath import TypedPath, IOObjectType
from .TimestampedPath import TimestampedPath

class LocalClearIO(IClearIO):
	HostName:str|None = None
	ShareName:str|None = None
	FullName:str|None = None

	def __init__(self) -> None:
		super().__init__()

	def Exists(self, fullPath:Path|str) -> True:
		if (isinstance(fullPath, str)):
			fullPath = Path(fullPath)
		return fullPath.exists()

	def CreateDirectory(self, fullDirectoryPath:Path|str, createParents:bool = True) -> None:
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		fullDirectoryPath.mkdir(parents=createParents, exist_ok=True)

	def RemoveDirectory(self, fullDirectoryPath:Path|str) -> None:
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.iterdir():
			if item.is_dir():
				self.RemoveDirectory(item)
			else:
				item.unlink()
		fullDirectoryPath.rmdir()

	def EmptyDirectory(self, fullDirectoryPath:Path|str) -> None:
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.iterdir():
			if item.is_dir():
				self.RemoveDirectory(item)
			else:
				item.unlink()

	def ListAllDirectories(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.iterdir():
			if (item.is_dir()):
				returnValue.append(TypedPath(item, IOObjectType.Directory))
		return sorted(returnValue)

	def ListAllDirectoriesRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.rglob("*"):
			if (item.is_dir()):
				returnValue.append(TypedPath(item, IOObjectType.Directory))
		return sorted(returnValue)

	def ListDirectories(self, fullDirectoryPath:Path|str, pattern:str|None = None) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		allItems:list[Path] = self.ListAllDirectories(fullDirectoryPath)
		if (pattern == "*.*" or pattern == "*" or pattern == "" or pattern is None):
			for item in allItems:
				returnValue.append(item)
		else:
			for item in allItems:
				if (re.fullmatch(pattern, str(item.stem))):
					returnValue.append(item)
		return sorted(returnValue)

	def ListDirectoriesRecursively(self, fullDirectoryPath:Path|str, pattern:str|None = None) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		allItems:list[Path] = self.ListAllDirectoriesRecursively(fullDirectoryPath)
		if (pattern == "*.*" or pattern == "*" or pattern == "" or pattern is None):
			for item in allItems:
				returnValue.append(item)
		else:
			for item in allItems:
				if (re.fullmatch(pattern, str(item.stem))):
					returnValue.append(item)
		return sorted(returnValue)

	def ListAllFilesModifiedSince(self, fullDirectoryPath:Path|str, sinceTimestamp:int) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.iterdir():
			if (item.is_file()
		 		and item.stat().st_mtime >= sinceTimestamp):
					returnValue.append(TypedPath(item, IOObjectType.File, item.stat().st_mtime))
		return sorted(returnValue)

	def ListAllFiles(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.iterdir():
			if (item.is_file()):
				returnValue.append(TypedPath(item, IOObjectType.File))
		return sorted(returnValue)

	def ListAllFilesRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.rglob("*"):
			if (item.is_file()):
				returnValue.append(TypedPath(item, IOObjectType.File))
		return sorted(returnValue)

	def ListFiles(self, fullDirectoryPath:Path|str, pattern:str|None = None) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		allItems:list[Path] = self.ListAllFiles(fullDirectoryPath)
		if (pattern == "*.*" or pattern == "*" or pattern == "" or pattern is None):
			for item in allItems:
				returnValue.append(item)
		else:
			for item in allItems:
				if (re.fullmatch(pattern, str(item.stem))):
					returnValue.append(item)
		return sorted(returnValue)

	def ListFilesRecursively(self, fullDirectoryPath:Path|str, pattern:str|None = None) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		allItems:list[Path] = self.ListAllFilesRecursively(fullDirectoryPath)
		if (pattern == "*.*" or pattern == "*" or pattern == "" or pattern is None):
			for item in allItems:
				returnValue.append(item)
		else:
			for item in allItems:
				if (re.fullmatch(pattern, str(item.stem))):
					returnValue.append(item)
		return sorted(returnValue)

	def List(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.glob("*"):
			returnValue.append(TypedPath(item, IOObjectType.File if item.is_file() else IOObjectType.Directory))
		return sorted(returnValue)

	def ListRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.rglob("*"):
			returnValue.append(TypedPath(item, IOObjectType.File if item.is_file() else IOObjectType.Directory))
		return sorted(returnValue)

	def GetFile(self, fullPath:Path|str) -> bytes:
		if (isinstance(fullPath, str)):
			fullPath = Path(fullPath)
		return fullPath.read_bytes()

	def PutFile(self, fullPath:Path|str, contents:bytes):
		if (isinstance(fullPath, str)):
			fullPath = Path(fullPath)
		fullPath.write_bytes(contents)

	def RemoveFile(self, fullFilePath:Path|str) -> None:
		if (isinstance(fullFilePath, str)):
			fullFilePath = Path(fullFilePath)
		if (fullFilePath.is_file):
			fullFilePath.unlink(True)

	def ParseTimestamps(self, paths:list[TypedPath], prefixesBeforeTimestamp:list[str] | None = None, timestampFormat:str | None = None) -> list[TimestampedPath]:
		returnValue:list[TimestampedPath] = list[TimestampedPath]()
		for item in paths:
			returnValue.append(TimestampedPath(item, prefixesBeforeTimestamp, timestampFormat))
		return sorted(returnValue)

__all__ = ["LocalClearIO"]
