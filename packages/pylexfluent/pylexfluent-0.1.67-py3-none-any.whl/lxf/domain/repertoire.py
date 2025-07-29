
import logging
from typing import List
from lxf.settings import get_logging_level
logger = logging.getLogger('Repertoire Office')
fh = logging.FileHandler('./logs/repertoire_office.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)
from pydantic import BaseModel,Field
from enum import StrEnum

class Nature(StrEnum):
    Brevet="BREVET"
    Minute="MINUTE"
    
class RepertoireNotaire(BaseModel):
    """
    Enregistrement d'un acte au répertoire
    """
    num_repertoire:str=Field(default="")
    date_signature:str=Field(default="")
    nature:Nature=Field(default=Nature.Minute)
    text:str=Field(default="")
    support:str=Field(default="")
    date_formalite:str=Field(default="")
    depot:str=Field(default="")
    frais_percus:str=Field(default="")
    droit_sur_etat:str=Field(default="")
    visa:str=Field(default="")
    numero_acte:str=Field(default="")
    clerc:str=Field(default="")