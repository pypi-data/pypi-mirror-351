from dataclasses import dataclass

@dataclass
class ImageFile(object):
  path:str
  extension:str

@dataclass
class ImageCompress(object):
  image:ImageFile