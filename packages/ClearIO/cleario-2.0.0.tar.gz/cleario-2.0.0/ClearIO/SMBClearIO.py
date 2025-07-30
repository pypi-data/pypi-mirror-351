from enum import Enum
from pathlib import Path
import platform
import re
from .IClearIO import IClearIO
from .TypedPath import TypedPath, IOObjectType
from .TimestampedPath import TimestampedPath

if (platform.system() == "Linux"):
	import smbclient
	import smbclient.shutil
if (platform.system() == "Windows"):
	import shutil
	import pywintypes
	import win32wnet

class WindowsSMBClearIO(IClearIO):
	HostName:str|None = None
	ShareName:str|None = None
	FullName:str|None = None

	def __init__(self, hostName:str, shareName:str, userName:str|None = None, password:str|None = None) -> None:
		super().__init__()
		self.HostName = hostName
		self.ShareName = shareName
		self.FullName = f"\\\\{hostName}\\{shareName}"
		netResource = win32wnet.NETRESOURCE()
		netResource.lpRemoteName = self.FullName
		win32wnet.WNetAddConnection2(netResource, password, userName, 0)

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
		return returnValue

	def ListAllDirectoriesRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.rglob("*"):
			if (item.is_dir()):
				returnValue.append(TypedPath(item, IOObjectType.Directory))
		return returnValue

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
		return returnValue

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
		return returnValue

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
		return returnValue

	def ListAllFilesRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.rglob("*"):
			if (item.is_file()):
				returnValue.append(TypedPath(item, IOObjectType.File))
		return returnValue

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
		return returnValue

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
		return returnValue

	def List(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.glob("*"):
			returnValue.append(TypedPath(item, IOObjectType.File if item.is_file() else IOObjectType.Directory))
		return returnValue

	def ListRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = Path(fullDirectoryPath)
		for item in fullDirectoryPath.rglob("*"):
			returnValue.append(TypedPath(item, IOObjectType.File if item.is_file() else IOObjectType.Directory))
		return returnValue

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
		return returnValue

class LinuxSMBClearIO(IClearIO):
	HostName:str|None = None
	ShareName:str|None = None
	FullName:str|None = None

	def __init__(self, hostName:str, shareName:str, userName:str|None = None, password:str|None = None) -> None:
		super().__init__()
		self.HostName = hostName
		self.ShareName = shareName
		self.FullName = f"\\\\{hostName}\\{shareName}"
		smbclient.register_session(self.HostName, username=userName, password=password)

	def Exists(self, fullPath:Path|str) -> True:
		if (isinstance(fullPath, Path)):
			fullPath = str(fullPath)
		return smbclient.path.exists(fullPath)

	def CreateDirectory(self, fullDirectoryPath:Path|str, createParents:bool = True) -> None:
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		lastSeparator:int = fullDirectoryPath.rfind("\\")
		if (not smbclient.path.exists(fullDirectoryPath)):
			if (smbclient.path.exists(fullDirectoryPath[:lastSeparator])):
				smbclient.mkdir(fullDirectoryPath)
			elif (createParents):
				smbclient.makedirs(fullDirectoryPath, True)
			else:
				raise FileNotFoundError("Parent directory not found")

	def RemoveDirectory(self, fullDirectoryPath:Path|str) -> None:
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		for item in smbclient.listdir(fullDirectoryPath):
			fullPath:str = f"{fullDirectoryPath}\\{item}"
			if (smbclient.path.isdir(fullPath)):
				self.RemoveDirectory(fullPath)
			else:
				smbclient.remove(fullPath)
		smbclient.rmdir(fullDirectoryPath)

	def EmptyDirectory(self, fullDirectoryPath:Path|str) -> None:
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		for item in smbclient.listdir(fullDirectoryPath):
			fullPath:str = f"{fullDirectoryPath}\\{item}"
			if (smbclient.path.isdir(fullPath)):
				self.RemoveDirectory(fullPath)

	def ListAllDirectories(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[Path|str] = list()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		for item in smbclient.listdir(fullDirectoryPath):
			fullPath:str = f"{fullDirectoryPath}\\{item}"
			if (smbclient.path.isdir(fullPath)):
				returnValue.append(TypedPath(fullPath, IOObjectType.Directory))
		return returnValue

	def ListAllDirectoriesRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[Path|str] = list()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		for item in smbclient.listdir(fullDirectoryPath):
			fullPath:str = f"{fullDirectoryPath}\\{item}"
			if (smbclient.path.isdir(fullPath)):
				returnValue.append(TypedPath(fullPath, IOObjectType.Directory))
				returnValue += self.ListAllDirectoriesRecursively(fullPath)
		return returnValue

	def ListDirectories(self, fullDirectoryPath:Path|str, pattern:str|None = None) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		allItems:list[Path] = self.ListAllDirectories(fullDirectoryPath)
		if (pattern == "*.*" or pattern == "*" or pattern == "" or pattern is None):
			for item in allItems:
				returnValue.append(item)
		else:
			for item in allItems:
				if (re.fullmatch(pattern, Path(item).stem)):
					returnValue.append(item)
		return returnValue

	def ListDirectoriesRecursively(self, fullDirectoryPath:Path|str, pattern:str|None = None) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		allItems:list[Path] = self.ListAllDirectoriesRecursively(fullDirectoryPath)
		if (pattern == "*.*" or pattern == "*" or pattern == "" or pattern is None):
			for item in allItems:
				returnValue.append(item)
		else:
			for item in allItems:
				if (re.fullmatch(pattern, Path(item).stem)):
					returnValue.append(item)
		return returnValue

	def ListAllFiles(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[Path|str] = list()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		for file in smbclient.listdir(fullDirectoryPath):
			fullPath:str = f"{fullDirectoryPath}\\{file}"
			if (smbclient.path.isfile(fullPath)):
				returnValue.append(TypedPath(fullPath, IOObjectType.File))
		return returnValue

	def ListAllFilesRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[Path|str] = list()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		directories:list[TypedPath] = self.ListDirectoriesRecursively(fullDirectoryPath)
		directories.append(fullDirectoryPath)
		for directory in directories:
			for file in smbclient.listdir(directory):
				fullPath:str = f"{directory}\\{file}"
				if (smbclient.path.isfile(fullPath)):
					returnValue.append(TypedPath(fullPath, IOObjectType.File))
		return returnValue

	def ListFiles(self, fullDirectoryPath:Path|str, pattern:str|None = None) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		allItems:list[Path] = self.ListAllFiles(fullDirectoryPath)
		if (pattern == "*.*" or pattern == "*" or pattern == "" or pattern is None):
			for item in allItems:
				returnValue.append(item)
		else:
			for item in allItems:
				if (re.fullmatch(pattern, Path(item).stem)):
					returnValue.append(item)
		return returnValue

	def ListFilesRecursively(self, fullDirectoryPath:Path|str, pattern:str|None = None) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		allItems:list[Path] = self.ListAllFilesRecursively(fullDirectoryPath)
		if (pattern == "*.*" or pattern == "*" or pattern == "" or pattern is None):
			for item in allItems:
				returnValue.append(item)
		else:
			for item in allItems:
				if (re.fullmatch(pattern, Path(item).stem)):
					returnValue.append(item)
		return returnValue

	def List(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[Path|str] = list()
		found:list[str] = list()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		for item in smbclient.listdir(fullDirectoryPath):
			fullPath:str = f"{fullDirectoryPath}\\{item}"
			returnValue.append(TypedPath(fullPath, IOObjectType.File if smbclient.path.isfile(fullPath) else IOObjectType.Directory))
		return returnValue

	def ListRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[Path|str] = list()
		found:list[str] = list()
		outputType:str = "Path" if (isinstance(fullDirectoryPath, Path)) else "str"
		if (isinstance(fullDirectoryPath, Path)):
			fullDirectoryPath = str(fullDirectoryPath)
		for item in smbclient.listdir(fullDirectoryPath):
			fullPath:str = f"{fullDirectoryPath}\\{item}"
			returnValue.append(TypedPath(fullPath, IOObjectType.File if smbclient.path.isfile(fullPath) else IOObjectType.Directory))
			if (smbclient.path.isdir(fullPath)):
				returnValue += self.ListRecursively(fullPath)
		return returnValue

	def GetFile(self, fullPath:Path|str) -> bytes:
		returnValue:bytes = bytes()
		if (isinstance(fullPath, Path)):
			fullPath = str(fullPath)
			with smbclient.open_file(fullPath, "r") as file:
				returnValue = file.read()
		return returnValue

	def PutFile(self, fullPath:Path|str, contents:bytes):
		if (isinstance(fullPath, Path)):
			fullPath = str(fullPath)
			with smbclient.open_file(fullPath, "w") as file:
				file.write(contents)

	def RemoveFile(self, fullFilePath:Path|str) -> None:
		if (isinstance(fullFilePath, Path)):
			fullFilePath = str(fullFilePath)
		if (smbclient.path.isfile(fullFilePath)):
			smbclient.remove(fullFilePath)

	def ParseTimestamps(self, paths:list[TypedPath], prefixesBeforeTimestamp:list[str] | None = None, timestampFormat:str | None = None) -> list[TimestampedPath]:
		returnValue:list[TimestampedPath] = list[TimestampedPath]()
		for item in paths:
			returnValue.append(TimestampedPath(item, prefixesBeforeTimestamp, timestampFormat))
		return returnValue

class SMBClearIO(IClearIO):
	"""
	Wrapper class for SMB access in a ClearIO compliant way.
	This class wraps SMB classes for either Windows or Linux SMB depending on which system it is ran on.
	"""

	smbClearIO:IClearIO|None = IClearIO()
	System:str = platform.system()

	def __init__(self, hostName:str, shareName:str, userName:str|None = None, password:str|None = None) -> None:
		"""
		Wrapper class for SMB access in a ClearIO compliant way.
		This class wraps SMB classes for either Windows or Linux SMB depending on which system it is ran on.
		

		Parameters
		----------
		hostName : str
			The name of the SMB (Windows or Samba on Linux) server.

		shareName : str
			The name of the SMB (Windows or Samba on Linux) share on the server.

		userName : str
			The user to connect to the SMB resource with.

		password : str
			The password for the user to connect to the SMB resource with.
		"""
		if (self.System == "Linux"):
			self.smbClearIO = LinuxSMBClearIO(hostName, shareName, userName, password)
		if (self.System == "Windows"):
			self.smbClearIO = WindowsSMBClearIO(hostName, shareName, userName, password)

	def Exists(self, fullPath:Path|str) -> True:
		return self.smbClearIO.Exists(fullPath)

	def CreateDirectory(self, fullDirectoryPath:Path|str, createParents:bool = True) -> None:
		self.smbClearIO.CreateDirectory(fullDirectoryPath, createParents)

	def RemoveDirectory(self, fullDirectoryPath:Path|str) -> None:
		self.smbClearIO.RemoveDirectory(fullDirectoryPath)

	def EmptyDirectory(self, fullDirectoryPath:Path|str) -> None:
		self.smbClearIO.EmptyDirectory(fullDirectoryPath)

	def ListDirectories(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		return sorted(self.smbClearIO.ListDirectories(fullDirectoryPath))

	def ListDirectoriesRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		return sorted(self.smbClearIO.ListDirectoriesRecursively(fullDirectoryPath))

	def ListAllFiles(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		return sorted(self.smbClearIO.ListAllFiles(fullDirectoryPath))

	def ListAllFilesRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		return sorted(self.smbClearIO.ListAllFilesRecursively(fullDirectoryPath))

	def ListFiles(self, fullDirectoryPath:Path|str, pattern:str|None = None) -> list[TypedPath]:
		return sorted(self.smbClearIO.ListFiles(fullDirectoryPath, pattern))

	def ListFilesRecursively(self, fullDirectoryPath:Path|str, pattern:str|None = None) -> list[TypedPath]:
		return sorted(self.smbClearIO.ListFilesRecursively(fullDirectoryPath, pattern))

	def List(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		return sorted(self.smbClearIO.List(fullDirectoryPath))

	def ListRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		return sorted(self.smbClearIO.ListRecursively(fullDirectoryPath))

	def GetFile(self, fullPath:Path|str) -> bytes:
		return self.smbClearIO.GetFile(fullPath)

	def PutFile(self, fullPath:Path|str, content:bytes):
		self.smbClearIO.PutFile(fullPath, content)

	def RemoveFile(self, fullFilePath:Path|str) -> None:
		self.smbClearIO.RemoveFile(fullFilePath)

	def ParseTimestamps(self, paths:list[TypedPath], prefixesBeforeTimestamp:list[str] | None = None, timestampFormat:str | None = None) -> list[TimestampedPath]:
		return sorted(self.smbClearIO.ParseTimestamps(paths, prefixesBeforeTimestamp, timestampFormat))

__all__ = ["WindowsSMBClearIO", "LinuxSMBClearIO", "SMBClearIO"]
