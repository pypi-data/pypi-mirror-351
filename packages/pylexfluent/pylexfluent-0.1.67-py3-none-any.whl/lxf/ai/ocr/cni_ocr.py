import os
import logging

from lxf.settings import get_logging_level, enable_tqdm

###################################################################

logger = logging.getLogger('cni ocr from PDF')
fh = logging.FileHandler('./logs/cni_ocr_from_pdf.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)
#################################################################
from pathlib import Path

from pdf2image import convert_from_path
from tqdm import tqdm

from lxf.services.measure_time import measure_time_async

from typing import List

from lxf.domain.cni import Cni
from lxf.ai.ocr.cni_utilities.recognize_zones import recognize

path_images_cni = "./data/images/temp/images-cni"

def check_path() ->None:
    """
    """
    data_path =Path("./data")
    if not data_path.exists: data_path.mkdir()
    image_path=Path("./data/images")    
    if not image_path.exists(): image_path.mkdir()
    temp_path=Path("./data/images/temp")
    if not temp_path.exists() : temp_path.mkdir()
    temp_document_path=Path(path_images_cni)
    if not temp_document_path.exists() : temp_document_path.mkdir()


@measure_time_async
async def do_cni_ocr_from_pdf(path_filename:str)->List[Cni]:
    """
    Paramètre le nom du fichier pdf contenant les CNI possibles
    retourne toutes les CNI trouvées
    """
    check_path()
    if os.path.exists(path_filename) ==False :
        logger.error(f"Fichier introuvable ({path_filename})")
        return None
    pages = convert_from_path(path_filename)
    cni_candidates:List[Cni]=[]
    for i in tqdm(range(len(pages)),desc="Analyse des pages ",disable=not enable_tqdm):
        ## Save image to file
        image_path = f"{path_images_cni}/page_{i}.jpeg"
        pages[i].save(image_path,'JPEG')    
        cni:Cni = recognize(image_path)
        if cni!=None :
            cni_candidates.append(cni)
    return cni_candidates

