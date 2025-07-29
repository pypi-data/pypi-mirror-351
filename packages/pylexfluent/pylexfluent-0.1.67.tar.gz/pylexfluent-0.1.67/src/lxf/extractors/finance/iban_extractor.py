
###################################################################

import logging
from lxf.domain.iban import  IbanCandidate
from lxf.settings import get_logging_level, load_model

logger = logging.getLogger('iban extractor')
fh = logging.FileHandler('./logs/iban_extractor.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)
#################################################################


from lxf.ai.ocr.iban_ocr import do_IBAN_Ocr_from_pdf
from lxf.extractors.finance.ibans.iban_analyzer import IbanAnalyzer
from lxf.services.try_safe import try_safe_execute_async

nlp = load_model()

async def extract_data(file_path:str,**kwargs)->tuple[str,list[IbanCandidate]]:
    """
    Extrait les données d'un iban 
    """

    if file_path==None: 
        logger.error("Extract Data: file_path ne peut pas etre None")
        return None, None
    text_ocr = await try_safe_execute_async(logger,do_IBAN_Ocr_from_pdf, path_filename=file_path)
    if text_ocr!=None :
        analyzer:IbanAnalyzer= IbanAnalyzer(text_ocr,nlp=nlp)
        return text_ocr, await try_safe_execute_async(logger,analyzer.do_analyze)
    return text_ocr, None