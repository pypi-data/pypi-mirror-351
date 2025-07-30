#RATEHIGHWAY_SFTP_HOST=sftp1.ratehighway.com
#RATEHIGHWAY_SFTP_PORT=22
#RATEHIGHWAY_SFTP_USERNAME=foxrac
#RATEHIGHWAY_SFTP_PASSWORD=FxrZjN!Ew8QX%Yb3
#RATEHIGHWAY_SFTP_SHOPDATA_DIRECTORY=/collection

from pathlib import Path
from ClearIO import SFTPClearIO, S3ClearIO, SFTPAuthenticationType, TypedPath, LocalClearIO

sftpHost:str = "sftp1.ratehighway.com"
sftpPort:int = 22
sftpUserName:str = "foxrac"
sftpPassword:str = "FxrZjN!Ew8QX%Yb3"
sftpDirectory:str = "/collection"

sftpClearIO = SFTPClearIO(hostName=sftpHost, port=sftpPort, authenticationType=SFTPAuthenticationType.Password, userName=sftpUserName, password=sftpPassword)
directories:list[TypedPath] = sftpClearIO.ListDirectories(sftpDirectory)
print(len(directories))
for directory in directories:
	print(f"Directory: {directory}")
	files:list[TypedPath] = sftpClearIO.ListFiles(directory)
	for file in files:
		print(f"\tFile: {file}")
		teee = sftpClearIO.GetFile(file)
		localClearIO:LocalClearIO = LocalClearIO()
		localClearIO.PutFile(Path(r"C:\Users\bmorris\source\repos\bradleydonmorris\ClearIO\tests\2025-01-21-88312-2.csv"),
				 sftpClearIO.GetFile(file))
		print(teee)
		break
	break
