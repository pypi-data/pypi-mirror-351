import datetime
from pydantic import BaseModel, Field

HIERARCHIE_DOCUMENT="document"
HIERARCHIE_DOSSIER="dossier"
HIERARCHIE_REPERTOIRE="repertoire"

class ExtractedMetadata (BaseModel):
    origine:str=Field(default="LEXIA")
    classe:str=Field(default="DIVERS") 
    classe_confidence:float=Field(default=0.0)
    documentId:str=Field(default="")
    traite_le:str=Field(default=str(datetime.datetime.today()))
    extra_metadata:dict=Field(default={})

class ChunkMetadata(BaseModel):
    chunk:int=Field(default=1)
    chunks:int=Field(default=1)
    title:str=Field(default="")
    description:str=Field(default="")
    source:str=Field(default="")
    hierarchie:str=Field(default=HIERARCHIE_DOCUMENT)
    extra_metadata:dict=Field(default={})


class Chunk(BaseModel):
    metadata:ChunkMetadata=Field(default=None)
    page_content:str=Field(default="")    
    summary:str=Field(default="")
    keywords:list[str]=[]
    explain:str=Field(default="")
class ExtractedData(BaseModel) :
    metadata:ExtractedMetadata=Field(default=None)
    chunks:list[Chunk]=[]
    keywords:list[str]=[]
    summary:str=Field(default="")
    explain:str=Field(default="")