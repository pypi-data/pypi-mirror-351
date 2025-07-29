import os
import shutil
import logging

from lxf.settings import get_logging_level

###################################################################

logger = logging.getLogger('test classifier')
fh = logging.FileHandler('./logs/test_classifier.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)
#################################################################
from lxf.ai.classification.multiclass.jupiter_model import MulticlassClassificationJupiterModel
from lxf.ai.ocr.ocr_pdf import do_ocr
from lxf.domain.keyWord import KeyWord
from lxf.domain.keyswordsandphrases import KeysWordsAndPhrases, KeysWordsPhrases
from lxf.domain.predictions import Predictions
from lxf.services.measure_time import measure_time_async
from lxf.services.pdf import get_text_and_tables_from_pdf
from lxf.services.try_safe import try_safe_execute, try_safe_execute_async
from multiprocessing import Process
from lxf.domain.tables import lxfTable


@measure_time_async
async def extract_text_from_file(file_name: str, max_pages: int = -1) -> str:
    """
    Extrait le texte du fichier PDF fourni en paramètre.
    """
    text, _ = await extract_text_and_table_from_file(file_name=file_name,extract_tables=False,layout=False,max_pages=max_pages)
    return text
    

@measure_time_async
async def extract_text_and_table_from_file(file_name: str,extract_text:bool=True,extract_tables:bool=True, layout:bool=False,max_pages: int = -1) -> tuple[str,list[lxfTable]]:
    """
    Extrait le texte du fichier PDF fourni en paramètre.
    """
    if os.path.exists(file_name) ==False:
        logger.error(f"Le fichier {file_name} n'existe pas !")
        return None
    result,tables = await try_safe_execute_async(logger,get_text_and_tables_from_pdf, filename=file_name,extract_text=extract_text,extract_tables=extract_tables,max_pages=max_pages,layout=layout)
    if result==None or result =='' and extract_text==True:
        # On a rien trouvé en lecture simple du document, essayons avec un OCR 
        output_filename = file_name.replace(".pdf","_ocr.pdf")
        # Pour l'OCR ouvrons un nouveau Process
        p=Process(target=do_ocr,args=(file_name,output_filename))
        p.start()
        p.join(120)
        if os.path.exists(output_filename):
            # Essayons à nouveau de récupérer le texte après OCR
            os.remove(file_name)
            shutil.copy(output_filename, file_name)
            os.remove(output_filename)
            result,tables = await try_safe_execute_async(logger,get_text_and_tables_from_pdf, filename=file_name,extract_tables=False,max_pages=max_pages, layout=layout)
    
    return result, tables

@measure_time_async
async def classify_text(text: str) -> Predictions:
    """
    Effectue la classification du texte fourni en paramètre.
    """
    if text == None or text == '':
        logger.warning("Texte vide ou invalide pour la classification.")
        return None

    keysWordsPhrasesHelper: KeysWordsAndPhrases = KeysWordsAndPhrases(text)
    freq_mots = keysWordsPhrasesHelper.get_key_words(isSorted=True, threshold=0.1)
    if freq_mots != None:
        # Convert data to KeysWordsPhrases object
        result:KeysWordsPhrases = KeysWordsPhrases()
        for mot in freq_mots:
            kword: KeyWord = KeyWord()
            kword.word = mot
            # logger.debug(f"Word: {mot}")
            kword.freq = freq_mots[mot]
            # logger.debug(f"Freq Word: {kword.freq}")
            result.keysWords.append(kword)
        if len(result.keysWords) > 0:
            jupiter: MulticlassClassificationJupiterModel = MulticlassClassificationJupiterModel()
            pred: Predictions = await try_safe_execute_async(logger, jupiter.inference, data=result, model_name="JupiterB1")
            return pred
        else:
            logger.warning("Aucune prediction trouvee")
            return None
    else:
        return None

@measure_time_async
async def get_classification(file_name: str, max_pages: int = -1) -> Predictions:
    """

    """
    # Extraction du texte
    result = await extract_text_from_file(file_name, max_pages)
    if result == None or result == '':
        logger.warning("Échec de l'extraction du texte.")
        return None

    # Classification du texte
    predictions = await classify_text(result)
    return predictions