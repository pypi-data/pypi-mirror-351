from enum import Enum
from pathlib import Path, PurePosixPath
import re
import io
import stat
from .IClearIO import IClearIO
from .TypedPath import TypedPath, IOObjectType
from .TimestampedPath import TimestampedPath

import warnings
from cryptography.utils import CryptographyDeprecationWarning
with warnings.catch_warnings(action="ignore", category=CryptographyDeprecationWarning):
	import paramiko
from paramiko import PKey
from paramiko import SFTPAttributes
from datetime import datetime

class SFTPAuthenticationType(Enum):
	Password = 1
	KeyFile = 2

class SFTPKeyType(Enum):
	DSSKey = 1
	RSAKey = 2
	Ed25519Key = 3
	ECDSAKey = 4

class SFTPClearIO(IClearIO):
	"""
	Class for SFTP access in a ClearIO compliant way.
	"""
	HostName:str|None = None
	Port:int = 22
	AuthenticationType:SFTPAuthenticationType = SFTPAuthenticationType.Password
	UserName:str|None = None
	Password:str|None = None
	KeyType:SFTPKeyType = SFTPKeyType.Ed25519Key
	KeyFile:Path|None = None
	Passphrase:str|None = None

	def __init__(self, hostName:str, port:int = 22,
			  authenticationType:SFTPAuthenticationType = SFTPAuthenticationType.Password,
			  userName:str|None = None,
			  password:str|None = None,
			  keyFile:Path|str|None = None,
			  keyType:SFTPKeyType = SFTPKeyType.RSAKey,
			  passphrase:str|None = None) -> None:
		if (hostName is None):
			raise ValueError("hostName is required")
		if (port is None):
			raise ValueError("port is required")
		if (authenticationType is None):
			raise ValueError("authenticationType is required")
		if (userName is None):
			raise ValueError("userName is required")
		self.HostName = hostName
		self.Port = port
		if (authenticationType == SFTPAuthenticationType.Password):
			if (userName is None):
				raise ValueError("If authenticationType is Password, then password is required")
			self.SetUserNamePasswordAuth(userName, password)
		if (authenticationType == SFTPAuthenticationType.KeyFile):
			if (keyFile is None):
				raise ValueError("keyFile is required")
			if (keyType is None):
				raise ValueError("keyType is required")
			self.SetKeyAuth(keyType, userName, keyFile, passphrase)

	def SetUserNamePasswordAuth(self, userName:str, password:str|None = None):
		self.AuthenticationType:SFTPAuthenticationType = SFTPAuthenticationType.Password
		self.UserName = userName
		self.Password = password

	def SetKeyAuth(self, keyType:SFTPKeyType, userName:str, keyFile:Path|str, passphrase:str|None = None):
		self.AuthenticationType:SFTPAuthenticationType = SFTPAuthenticationType.KeyFile
		self.KeyType = keyType
		self.UserName = userName
		if (isinstance(keyFile, str)):
			self.KeyFile = Path(keyFile)
		else:
			self.KeyFile = keyFile
		self.Passphrase = passphrase

	def __GetKey__(self) -> PKey:
		match self.KeyType:
			case SFTPKeyType.DSSKey:
				return paramiko.DSSKey.from_private_key_file(self.KeyFile, self.Passphrase)
			case SFTPKeyType.RSAKey:
				return paramiko.RSAKey.from_private_key_file(self.KeyFile, self.Passphrase)
			case SFTPKeyType.Ed25519Key:
				return paramiko.Ed25519Key.from_private_key_file(self.KeyFile, self.Passphrase)
			case SFTPKeyType.ECDSAKey:
				return paramiko.ECDSAKey.from_private_key_file(self.KeyFile, self.Passphrase)

	def Exists(self, fullPath:Path|str) -> True:
		returnValue:bool = False
		try:
			if (not isinstance(fullPath, str)):
				fullPath = str(fullPath)
			if (fullPath == "." or fullPath == ""):
				fullPath = "/"
			with paramiko.Transport((self.HostName, self.Port)) as transport:
				match self.AuthenticationType:
					case SFTPAuthenticationType.Password:
						transport.connect(username=self.UserName, password=self.Password)
					case SFTPAuthenticationType.KeyFile:
						transport.connect(username=self.UserName, pkey=self.__GetKey__())
				with paramiko.SFTPClient.from_transport(transport) as sftp:
					with io.BytesIO() as contentsIO:
						sftp.stat(fullPath)
						returnValue = True
		except:
			returnValue = False
		return returnValue

	def CreateDirectory(self, fullDirectoryPath:Path|str, createParents:bool = True) -> None:
		exception = None
		try:
			if (not isinstance(fullDirectoryPath, str)):
				fullDirectoryPath = str(fullDirectoryPath)
			if (fullDirectoryPath == "." or fullDirectoryPath == ""):
				fullDirectoryPath = "/"
			with paramiko.Transport((self.HostName, self.Port)) as transport:
				match self.AuthenticationType:
					case SFTPAuthenticationType.Password:
						transport.connect(username=self.UserName, password=self.Password)
					case SFTPAuthenticationType.KeyFile:
						transport.connect(username=self.UserName, pkey=self.__GetKey__())
				with paramiko.SFTPClient.from_transport(transport) as sftp:
					fullPath:PurePosixPath = PurePosixPath(fullDirectoryPath)
					exists:bool = True
					try:
						stat:SFTPAttributes = sftp.stat(str(fullPath))
						exists = True
					except:
						exists = False
					if (not exists):
						try:
							statParent:SFTPAttributes = sftp.stat(str(fullPath.parent))
							exists = True
						except:
							exists = False
						if (exists):
							sftp.mkdir(str(fullPath))
						elif (createParents):
							currentPath:str = ""
							pathElements:list[str] = str(fullPath)[1:].split("/")
							for directory in pathElements:
								currentPath += f"/{directory}"
								exists = False
								try:
									statParent:SFTPAttributes = sftp.stat(currentPath)
									exists = True
								except:
									exists = False
								if (not exists):
									sftp.mkdir(currentPath)
		except Exception as e:
			exception = e
		if (exception is not None):
			raise exception

	def RemoveDirectory(self, fullDirectoryPath:Path|str) -> None:
		exception = None
		try:
			if (not isinstance(fullDirectoryPath, str)):
				fullDirectoryPath = str(fullDirectoryPath)
			if (fullDirectoryPath == "." or fullDirectoryPath == ""):
				fullDirectoryPath = "/"
			with paramiko.Transport((self.HostName, self.Port)) as transport:
				match self.AuthenticationType:
					case SFTPAuthenticationType.Password:
						transport.connect(username=self.UserName, password=self.Password)
					case SFTPAuthenticationType.KeyFile:
						transport.connect(username=self.UserName, pkey=self.__GetKey__())
				with paramiko.SFTPClient.from_transport(transport) as sftp:
					for item in sftp.listdir_attr(fullDirectoryPath):
						fullPath:PurePosixPath = PurePosixPath(fullDirectoryPath).joinpath(item.filename)
						if (stat.S_ISDIR(item.st_mode)):
							self.RemoveDirectory(fullPath)
						else:
							sftp.unlink(fullPath)
					sftp.rmdir(fullDirectoryPath)
		except Exception as e:
			exception = e
		if (exception is not None):
			raise exception

	def EmptyDirectory(self, fullDirectoryPath:Path|str) -> None:
		exception = None
		try:
			if (not isinstance(fullDirectoryPath, str)):
				fullDirectoryPath = str(fullDirectoryPath)
			if (fullDirectoryPath == "." or fullDirectoryPath == ""):
				fullDirectoryPath = "/"
			with paramiko.Transport((self.HostName, self.Port)) as transport:
				match self.AuthenticationType:
					case SFTPAuthenticationType.Password:
						transport.connect(username=self.UserName, password=self.Password)
					case SFTPAuthenticationType.KeyFile:
						transport.connect(username=self.UserName, pkey=self.__GetKey__())
				with paramiko.SFTPClient.from_transport(transport) as sftp:
					item:SFTPAttributes = sftp.stat(fullDirectoryPath)
					if (stat.S_ISDIR(item.st_mode)):
						self.RemoveDirectory(fullDirectoryPath)
		except Exception as e:
			exception = e
		if (exception is not None):
			raise exception

	def ListAllDirectories(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (not isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = str(fullDirectoryPath)
		if (fullDirectoryPath == "." or fullDirectoryPath == ""):
			fullDirectoryPath = "/"
		with paramiko.Transport((self.HostName, self.Port)) as transport:
			match self.AuthenticationType:
				case SFTPAuthenticationType.Password:
					transport.connect(username=self.UserName, password=self.Password)
				case SFTPAuthenticationType.KeyFile:
					transport.connect(username=self.UserName, pkey=self.__GetKey__())
			with paramiko.SFTPClient.from_transport(transport) as sftp:
				for item in sftp.listdir_attr(fullDirectoryPath):
					fullPath:PurePosixPath = PurePosixPath(fullDirectoryPath).joinpath(item.filename)
					if (stat.S_ISDIR(item.st_mode)):
						returnValue.append(TypedPath(fullPath, IOObjectType.Directory))
		return sorted(returnValue)

	def ListAllDirectoriesRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (not isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = str(fullDirectoryPath)
		if (fullDirectoryPath == "." or fullDirectoryPath == ""):
			fullDirectoryPath = "/"
		with paramiko.Transport((self.HostName, self.Port)) as transport:
			match self.AuthenticationType:
				case SFTPAuthenticationType.Password:
					transport.connect(username=self.UserName, password=self.Password)
				case SFTPAuthenticationType.KeyFile:
					transport.connect(username=self.UserName, pkey=self.__GetKey__())
			with paramiko.SFTPClient.from_transport(transport) as sftp:
				for item in sftp.listdir_attr(fullDirectoryPath):
					fullPath:PurePosixPath = PurePosixPath(fullDirectoryPath).joinpath(item.filename)
					if (stat.S_ISDIR(item.st_mode)):
						returnValue.append(TypedPath(fullPath, IOObjectType.Directory))
						returnValue += self.ListFilesRecursively(fullPath)
		return sorted(returnValue)

	def ListDirectories(self, fullDirectoryPath:Path|str, pattern:str|None = None) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (not isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = str(fullDirectoryPath)
		if (fullDirectoryPath == "." or fullDirectoryPath == ""):
			fullDirectoryPath = "/"
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
		if (not isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = str(fullDirectoryPath)
		if (fullDirectoryPath == "." or fullDirectoryPath == ""):
			fullDirectoryPath = "/"
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
		if (not isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = str(fullDirectoryPath)
		if (fullDirectoryPath == "." or fullDirectoryPath == ""):
			fullDirectoryPath = "/"
		with paramiko.Transport((self.HostName, self.Port)) as transport:
			match self.AuthenticationType:
				case SFTPAuthenticationType.Password:
					transport.connect(username=self.UserName, password=self.Password)
				case SFTPAuthenticationType.KeyFile:
					transport.connect(username=self.UserName, pkey=self.__GetKey__())
			with paramiko.SFTPClient.from_transport(transport) as sftp:
				for item in sftp.listdir_attr(fullDirectoryPath):
					fullPath:PurePosixPath = PurePosixPath(fullDirectoryPath).joinpath(item.filename)
					if (not stat.S_ISDIR(item.st_mode)
		 				and item.st_mtime >= sinceTimestamp):
						returnValue.append(TypedPath(fullPath, IOObjectType.File, item.st_mtime))
		return sorted(returnValue)

	def ListAllFiles(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (not isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = str(fullDirectoryPath)
		if (fullDirectoryPath == "." or fullDirectoryPath == ""):
			fullDirectoryPath = "/"
		with paramiko.Transport((self.HostName, self.Port)) as transport:
			match self.AuthenticationType:
				case SFTPAuthenticationType.Password:
					transport.connect(username=self.UserName, password=self.Password)
				case SFTPAuthenticationType.KeyFile:
					transport.connect(username=self.UserName, pkey=self.__GetKey__())
			with paramiko.SFTPClient.from_transport(transport) as sftp:
				for item in sftp.listdir_attr(fullDirectoryPath):
					fullPath:PurePosixPath = PurePosixPath(fullDirectoryPath).joinpath(item.filename)
					if (not stat.S_ISDIR(item.st_mode)):
						returnValue.append(TypedPath(fullPath, IOObjectType.File))
		return sorted(returnValue)

	def ListAllFilesRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (not isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = str(fullDirectoryPath)
		if (fullDirectoryPath == "." or fullDirectoryPath == ""):
			fullDirectoryPath = "/"
		with paramiko.Transport((self.HostName, self.Port)) as transport:
			match self.AuthenticationType:
				case SFTPAuthenticationType.Password:
					transport.connect(username=self.UserName, password=self.Password)
				case SFTPAuthenticationType.KeyFile:
					transport.connect(username=self.UserName, pkey=self.__GetKey__())
			with paramiko.SFTPClient.from_transport(transport) as sftp:
				for item in sftp.listdir_attr(fullDirectoryPath):
					fullPath:PurePosixPath = PurePosixPath(fullDirectoryPath).joinpath(item.filename)
					if (not stat.S_ISDIR(item.st_mode)):
						returnValue.append(TypedPath(fullPath, IOObjectType.File))
					else:
						returnValue += self.ListFilesRecursively(fullPath)
		return sorted(returnValue)

	def ListFiles(self, fullDirectoryPath:Path|str, pattern:str|None = None) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (not isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = str(fullDirectoryPath)
		if (fullDirectoryPath == "." or fullDirectoryPath == ""):
			fullDirectoryPath = "/"
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
		if (not isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = str(fullDirectoryPath)
		if (fullDirectoryPath == "." or fullDirectoryPath == ""):
			fullDirectoryPath = "/"
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
		if (not isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = str(fullDirectoryPath)
		if (fullDirectoryPath == "." or fullDirectoryPath == ""):
			fullDirectoryPath = "/"
		with paramiko.Transport((self.HostName, self.Port)) as transport:
			match self.AuthenticationType:
				case SFTPAuthenticationType.Password:
					transport.connect(username=self.UserName, password=self.Password)
				case SFTPAuthenticationType.KeyFile:
					transport.connect(username=self.UserName, pkey=self.__GetKey__())
			with paramiko.SFTPClient.from_transport(transport) as sftp:
				for item in sftp.listdir_attr(fullDirectoryPath):
					fullPath:PurePosixPath = PurePosixPath(fullDirectoryPath).joinpath(item.filename)
					returnValue.append(TypedPath(fullPath, IOObjectType.Directory if stat.S_ISDIR(item.st_mode) else IOObjectType.File))
		return sorted(returnValue)

	def ListRecursively(self, fullDirectoryPath:Path|str) -> list[TypedPath]:
		returnValue:list[TypedPath] = list[TypedPath]()
		if (not isinstance(fullDirectoryPath, str)):
			fullDirectoryPath = str(fullDirectoryPath)
		if (fullDirectoryPath == "." or fullDirectoryPath == ""):
			fullDirectoryPath = "/"
		with paramiko.Transport((self.HostName, self.Port)) as transport:
			match self.AuthenticationType:
				case SFTPAuthenticationType.Password:
					transport.connect(username=self.UserName, password=self.Password)
				case SFTPAuthenticationType.KeyFile:
					transport.connect(username=self.UserName, pkey=self.__GetKey__())
			with paramiko.SFTPClient.from_transport(transport) as sftp:
				for item in sftp.listdir_attr(fullDirectoryPath):
					fullPath:PurePosixPath = PurePosixPath(fullDirectoryPath).joinpath(item.filename)
					returnValue.append(TypedPath(fullPath, IOObjectType.Directory if stat.S_ISDIR(item.st_mode) else IOObjectType.File))
					if (stat.S_ISDIR(item.st_mode)):
						returnValue += self.ListRecursively(fullPath)
		return sorted(returnValue)

	def GetFile(self, fullFilePath:Path|str) -> bytes:
		returnValue:bytes = bytes()
		exception = None
		try:
			if (not isinstance(fullFilePath, str)):
				fullFilePath = str(fullFilePath)
			if (fullFilePath == "." or fullFilePath == ""):
				fullFilePath = "/"
			with paramiko.Transport((self.HostName, self.Port)) as transport:
				match self.AuthenticationType:
					case SFTPAuthenticationType.Password:
						transport.connect(username=self.UserName, password=self.Password)
					case SFTPAuthenticationType.KeyFile:
						transport.connect(username=self.UserName, pkey=self.__GetKey__())
				with paramiko.SFTPClient.from_transport(transport) as sftp:
					with sftp.open(fullFilePath, "rb") as remoteFile:
						returnValue = remoteFile.read()
					#with io.BytesIO() as contentsIO:
					#	sftp.getfo(fullFilePath, contentsIO)
					#	returnValue = contentsIO.read()
		except Exception as e:
			exception = e
		if (exception is not None):
			raise exception
		if (returnValue is not None):
			return returnValue

	def PutFile(self, fullFilePath:Path|str, contents:bytes):
		exception = None
		try:
			if (not isinstance(fullFilePath, str)):
				fullFilePath = str(fullFilePath)
			if (fullFilePath == "." or fullFilePath == ""):
				fullFilePath = "/"
			with paramiko.Transport((self.HostName, self.Port)) as transport:
				match self.AuthenticationType:
					case SFTPAuthenticationType.Password:
						transport.connect(username=self.UserName, password=self.Password)
					case SFTPAuthenticationType.KeyFile:
						transport.connect(username=self.UserName, pkey=self.__GetKey__())
				with paramiko.SFTPClient.from_transport(transport) as sftp:
					with sftp.open(fullFilePath, "wb") as remoteFile:
						remoteFile.write(contents)
					#with io.BytesIO() as contentsIO:
					#	contentsIO.write(contents)
					#	contentsIO.flush()
					#	sftp.putfo(contentsIO, fullFilePath)
		except Exception as e:
			exception = e
		if (exception is not None):
			raise exception

	def RemoveFile(self, fullFilePath:Path|str) -> None:
		exception = None
		try:
			if (not isinstance(fullFilePath, str)):
				fullFilePath = str(fullFilePath)
			if (fullFilePath == "." or fullFilePath == ""):
				fullFilePath = "/"
			with paramiko.Transport((self.HostName, self.Port)) as transport:
				match self.AuthenticationType:
					case SFTPAuthenticationType.Password:
						transport.connect(username=self.UserName, password=self.Password)
					case SFTPAuthenticationType.KeyFile:
						transport.connect(username=self.UserName, pkey=self.__GetKey__())
				with paramiko.SFTPClient.from_transport(transport) as sftp:
					item:SFTPAttributes = sftp.stat(fullFilePath)
					if (not stat.S_ISDIR(item.st_mode)):
						sftp.unlink(fullFilePath)
		except Exception as e:
			exception = e
		if (exception is not None):
			raise exception

	def ParseTimestamps(self, paths:list[str|Path], prefixesBeforeTimestamp:list[str] | None = None, timestampFormat:str | None = None) -> list[TimestampedPath]:
		returnValue:list[TimestampedPath] = list[TimestampedPath]()
		for item in paths:
			returnValue.append(TimestampedPath(item, prefixesBeforeTimestamp, timestampFormat))
		return sorted(returnValue)

	def GetFileProperties(self, filePath:Path|str) -> dict:
		returnValue:dict|None = None
		try:
			if (not isinstance(filePath, str)):
				filePath = str(filePath)
			if (filePath == "." or filePath == ""):
				filePath = "/"
			with paramiko.Transport((self.HostName, self.Port)) as transport:
				match self.AuthenticationType:
					case SFTPAuthenticationType.Password:
						transport.connect(username=self.UserName, password=self.Password)
					case SFTPAuthenticationType.KeyFile:
						transport.connect(username=self.UserName, pkey=self.__GetKey__())
				with paramiko.SFTPClient.from_transport(transport) as sftp:
					sftpAttributes:SFTPAttributes = sftp.stat(filePath)
					returnValue = {
						"st_size": sftpAttributes.st_size,
						"st_uid": sftpAttributes.st_uid,
						"st_gid": sftpAttributes.st_gid,
						"st_mode": sftpAttributes.st_mode,
						"st_atime": sftpAttributes.st_atime,
						"st_mtime": sftpAttributes.st_mtime,
						"ModifiedTimestamp": sftpAttributes.st_mtime,
						"ModifiedTime": datetime.fromtimestamp(sftpAttributes.st_mtime)
					}
		except:
			returnValue = None
		return returnValue

__all__ = ["SFTPAuthenticationType", "SFTPKeyType", "SFTPClearIO"]
