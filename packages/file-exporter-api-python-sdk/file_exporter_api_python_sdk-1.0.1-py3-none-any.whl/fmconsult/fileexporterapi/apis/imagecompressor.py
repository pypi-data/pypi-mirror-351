import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from fmconsult.fileexporterapi.api import FileExporterApi
from fmconsult.fileexporterapi.dtos.image import ImageCompress

class ImageCompressor(FileExporterApi):
  
  def compress(self, image:ImageCompress):
   try:
      logging.info(f'compressing image file...')
      url = UrlUtil().make_url(self.base_url, ['image', 'compress'])
      res = self.call_request(HTTPMethod.POST, url, None, payload=image)
      return jsonpickle.decode(res)
   except:
     raise