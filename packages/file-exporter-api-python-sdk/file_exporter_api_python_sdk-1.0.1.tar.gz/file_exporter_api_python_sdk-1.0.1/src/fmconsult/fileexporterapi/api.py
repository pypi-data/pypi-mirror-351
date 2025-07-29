import os
from fmconsult.http.api import ApiBase

class FileExporterApi(ApiBase):

  def __init__(self):
    try:
      self.api_token = os.environ['fmconsult.file-exporter.api.token']
      self.base_url = 'https://api-file-exporter.fmconsult.com.br/v2'
      super().__init__()
    except:
      raise