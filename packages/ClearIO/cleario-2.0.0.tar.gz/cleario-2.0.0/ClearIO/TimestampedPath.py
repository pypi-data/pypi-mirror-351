from datetime import datetime
import pathlib
from .TypedPath import TypedPath

class TimestampedPath(TypedPath):
	Timestamp:datetime|None = None
	TimestampString:str|None = None
	HasTimestamp:bool = False	

	def __init__(self, path:TypedPath, prefixesBeforeTimestamp:list[str] | None = None, timestampFormat:str | None = None):
		if (isinstance(path, pathlib.Path)):
			super().__init__(str(path))
		else:
			super().__init__(path)
		try:
			timestampLength:int = len(datetime.now().strftime(timestampFormat))
			fileName:str = str(super().stem)
			if (prefixesBeforeTimestamp is not None and len(prefixesBeforeTimestamp) > 0):
				for prefix in prefixesBeforeTimestamp:
					if (prefix == "" or prefix is None):
						if (len(fileName) == timestampLength):
							self.TimestampString = fileName
							self.Timestamp = datetime.strptime(self.TimestampString, timestampFormat)
					elif (fileName.startswith(prefix)):
						timestampString:str = str(fileName)[len(prefix):len(prefix)+timestampLength]
						self.TimestampString = timestampString
						self.Timestamp = datetime.strptime(self.TimestampString, timestampFormat)
						break
			else:
				if (len(fileName) == timestampLength):
					self.TimestampString = fileName
					self.Timestamp = datetime.strptime(self.TimestampString, timestampFormat)
			if (self.Timestamp is None):
				self.TimestampString = None
				self.HasTimestamp = False
			else:
				self.HasTimestamp = True
		except:
			self.HasTimestamp = False	

	def __str__(self):
		return str(super().__str__())

__all__ = ["TimestampedPath"]
