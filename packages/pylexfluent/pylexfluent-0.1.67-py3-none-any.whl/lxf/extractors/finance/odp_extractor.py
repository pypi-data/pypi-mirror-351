
import logging
from multiprocessing import Process
import os 
from lxf.settings import get_logging_level

###################################################################

logger = logging.getLogger('odp_extractor')
fh = logging.FileHandler('./logs/odp_extractor.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)
#################################################################

from lxf.ai.ocr.ocr_pdf import do_ocr
from lxf.services.measure_time import measure_time_async
from lxf.extractors.finance.loans.loan_extractor import LoanDataExtractor
from lxf.services.try_safe import try_safe_execute_async

@measure_time_async
async def extract_data(file_path:str,**kwargs)->str|None:
    """
    Extrait les données d'une offre de prêt 
    """
    if file_path==None: 
        logger.error("Extract Data: file_path ne peut pas etre None")
        return None
    logger.debug(f"Demande extraction de donnees pour {file_path}")
    loan:LoanDataExtractor= LoanDataExtractor(file_path)
    result= await try_safe_execute_async(logger,loan.extract_data)
    if result!=None:
        logger.debug(f"Extraction de donnees different de None ? {result!=None}")     
    else :
        logger.warning("Extraction retourne aucune donnée, on essaye en faisant un OCR du document ")
        # On a rien trouvé en lecture simple du document, essayons avec un OCR 
        output_filename = file_path.replace(".pdf","_ocr.pdf")
        # Pour l'OCR ouvrons un nouveau Process
        p=Process(target=do_ocr,args=(file_path,output_filename))
        p.start()
        p.join()
        # Essayons à nouveau extraction après OCR
        loan= LoanDataExtractor(output_filename)
        result = await try_safe_execute_async(logger,loan.extract_data)
        if os.path.exists(output_filename) :
            # Supprimons le fichier temporaire
            os.remove(output_filename)           
    return result
