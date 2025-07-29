import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from fmconsult.fileexporterapi.api import FileExporterApi
from fmconsult.fileexporterapi.dtos.excel import ExcelExport, ExcelConvert

class FileGenerator(FileExporterApi):

  def generate_pdf_from_url(self, url):
    try:
      logging.info(f'generating PDF file from url {url}...')
      url = UrlUtil().make_url(self.base_url, ['export', 'pdf'])
      data = {
        'path': url
      }
      res = self.call_request(HTTPMethod.POST, url, None, payload=data)
      return jsonpickle.decode(res)
    except:
      raise

  def generate_excel_file(self, data:ExcelExport):
    try:
      logging.info(f'generating Excel file...')
      url = UrlUtil().make_url(self.base_url, ['export', 'excel'])
      res = self.call_request(HTTPMethod.POST, url, None, payload=data.__dict__)
      res = jsonpickle.decode(res)
      res['filename'] = f"{self.base_url}/{res['filename']}"
      return res
    except:
      raise

  def convert_excel_to_json(self, data:ExcelConvert):
    try:
      url = UrlUtil().make_url(self.base_url, ['export', 'excel', 'json'])
      logging.info(f'reading Excel file and interpolate to JSON...')
      res = self.call_request(HTTPMethod.POST, url, None, payload=data.__dict__)
      return jsonpickle.decode(res)
    except:
      raise