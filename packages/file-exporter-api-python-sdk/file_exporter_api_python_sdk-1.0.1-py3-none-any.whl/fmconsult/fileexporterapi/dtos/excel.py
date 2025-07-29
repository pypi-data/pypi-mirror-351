from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any

class ColumnTypes(Enum):
  INT      = "INT"
  DOUBLE   = "DOUBLE"
  DATE     = "DATE"
  DATETIME = "DATETIME"
  MONEY    = "MONEY"
  GENERAL  = "GENERAL"

@dataclass
class Column(object):
  nome_coluna:str
  titulo:str
  index:int
  tipo:ColumnTypes

@dataclass
class ExcelExport(object):
  template_name:str
  colunas:List[Column]
  dados:List[Dict[str, Any]]

class ExcelFileType(Enum):
  EXCEL_97_2003 = "xls"
  EXCEL_2010    = "xlsx"

@dataclass
class ExcelConvert(object):
  date_format:str
  file_content:str
  file_type:ExcelFileType