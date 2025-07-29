
import logging
from typing import List

from lxf.settings import get_logging_level

logger = logging.getLogger('cni Extractor')
fh = logging.FileHandler('./logs/cni_extractor.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)

from lxf.domain.cni import Cni
from lxf.ai.ocr.cni_ocr import do_cni_ocr_from_pdf
from lxf.services.try_safe import try_safe_execute_async

async def extract_data(file_path:str)->Cni:
    """
    Extrait les données d'une cni 
    """
    if file_path==None: 
        logger.error("Extract Data: file_path ne peut pas etre None")
        return None
    result:List[Cni] = await try_safe_execute_async(logger,do_cni_ocr_from_pdf, path_filename=file_path)    
    return result