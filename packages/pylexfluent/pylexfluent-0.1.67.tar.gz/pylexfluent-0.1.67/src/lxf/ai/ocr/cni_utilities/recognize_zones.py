import os

import logging
import re


from lxf.settings import get_logging_level

logger = logging.getLogger('cni recognize')
fh = logging.FileHandler('./logs/cni_recognize.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)

from typing import Tuple
import cv2
from cv2.typing import MatLike


from lxf.domain.cni import Cni
from lxf.domain.cni_zones import CniDetectedZone
from lxf.services.measure_time import measure_time
from lxf.ai.ocr.cni_utilities.detection.cni_detection import detection , detectFront, detectBack
from lxf.ai.ocr.text_extractor import extract_text_from_image


def extract_id_number(text: str) -> str:
    """
    Extrait le numéro d'identité à partir du texte OCR.
    """
    match = re.search(r'\b\d{8,}\b', text)

    return match.group(0) if match else None

def extract_personal_info(text: str) -> Tuple[str, str]:
    """
    Extrait le nom, le prénom à partir du texte OCR.
    """
    # Cherche le prénom et le nom
    first_name = None
    last_name = None
    match_name = re.search(r"Prénom(?:\(s\))?\s*:?\s*(.+)", text, re.IGNORECASE)
    if match_name:
        first_name = match_name.group(1).strip()

    match_last_name = re.search(r"Nom\s*:?\s*([A-ZÉÈÀ'\-\.]+(?:\sEpouse\s[A-ZÉÈÀ'\-\.]+)?)", text, re.IGNORECASE)
    if match_last_name:
        last_name = match_last_name.group(1).strip()

    return first_name, last_name


def extract_birth_date(text:str)->str:
    """
    Extrait la date de naissance a partir du texte OCR
    """
    match_date = re.search(
    r"N[ée]?\(?e?\)?\s*le[:;]?\s*(\d{2}[\.\s]\d{2}[\.\s]?\d{4})", 
    text, 
    re.IGNORECASE
)
    if match_date:
        return match_date.group(1).replace(" ", ".")
    return None

def extract_dates(text: str) -> Tuple[str, str]:
    """
    Extrait deux dates d'un texte et les attribue :
    - La première date trouvée est "valable jusqu'à".
    - La deuxième date trouvée est "délivré le".
    """
    dates = re.findall(r"\d{2}\s*[.,]\s*\d{2}\s*[.,]?\s*\d{4}", text)
    
    standardized_dates = [date.replace(" ", ".").replace(",", ".") for date in dates]
    
    expiry_date = standardized_dates[0] if len(standardized_dates) > 0 else None
    issue_date = standardized_dates[1] if len(standardized_dates) > 1 else None

    return expiry_date, issue_date


def extract_address(text: str) -> str:
    """
    Extrait l'adresse à partir d'un texte OCR.
    
    """
    match = re.search(
        r"[Aa]dresse\s*:?\s*(.+?)\s*(Carte valable jusqu'au|délivrée le)", 
        text
    )
    if match:
        return match.group(1).strip()
    return None

@measure_time
def recognize(filename: str) -> Cni:
    """
        Applique l'OCR sur une image de CNI pour extraire ses informations.
        return: Cni
    """
    if not os.path.exists(filename):
        msg = f"Le fichier {filename} n'existe pas"
        logger.error(msg)
        raise Exception(msg)
    
    result: CniDetectedZone = detection(filename)
    if result is None:
        logger.error(f"Aucune zone détectée ({filename})")
        return None
    
    cni = Cni(is_recto=result.is_recto)


    if result.is_recto:
        # Traitement du recto
        zones = detectFront(result)
        if zones is None:
            logger.error(f"Aucune zone détectée pour le recto ! {filename}")
            return None
        
        # Zone ID
        source = zones.id
        id_image = process_image(source)

        if id_image.any:
            id_text = extract_text_from_image(id_image)
            cni.id_number = extract_id_number(id_text)
        
        # Zone Informations (nom, prénom, etc.)
        source = zones.info
        info_image = process_image(source)

        if info_image.any:
            info_text = extract_text_from_image(info_image)
            cni.first_name, cni.last_name= extract_personal_info(info_text)
        
        # Zone MRZ
        source = zones.mrz
        mrz_image = process_image(source)

        if mrz_image.any:
            mrz_text = extract_text_from_image(mrz_image,use_tesseract=False)
            cni.mrz= mrz_text.strip().replace(" ","")
        

        #zone date naissance
        source = zones.dat_of_birth
        date_image=process_image(source)
        if date_image.any:
            date_text = extract_text_from_image(date_image)
            date_text=extract_birth_date(date_text)
            cni.date_of_birth=date_text

    else:
        # Traitement du verso
        info = detectBack(result.image)
        verso = process_image_verso(info)

        if verso.any:
            verso_text = extract_text_from_image(verso,
                                                 use_tesseract=False)
            expiry_date, issue_date=extract_dates(verso_text)
            cni.expiry_date=expiry_date
            cni.issue_date=issue_date
            cni.address=extract_address(verso_text)
            
    
    return cni

@measure_time
def process_image_verso(source)->MatLike:
    """
    Prétraite le verso de la cni pour l'OCR.
    :param img: Image source.
    :return: Image prétraitée.
    """
    if source is None or source.size == 0:
        raise Exception(f"L'image source {source} est vide ou non initialisée.")

    logger.debug(f"Dimensions de l'image avant traitement : {source.shape}")

    gray: MatLike = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    if gray is None or gray.size == 0:
        raise Exception("Erreur lors de la conversion en niveaux de gris.")

    final:MatLike=cv2.bilateralFilter(gray, 11,75,75)
    thresh = cv2.adaptiveThreshold(
        final, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    return thresh


@measure_time
def apply_truncate_filter(img: MatLike) -> MatLike:
    """
    Applique un filtre Truncate pour réduire le bruit.
    :param img: Image source.
    :return: Image filtrée.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    _, truncate_img = cv2.threshold(gray, 140, 255, cv2.THRESH_TRUNC)
    
    return truncate_img


def process_image(img: MatLike) -> MatLike:

    """
    Prétraite une image pour l'OCR.
    :param img: Image source.
    :return: Image prétraitée.
    """
    if img is None or img.size == 0:
        raise Exception(f"L'image source {img}est vide ou non initialisée.")
    
    truncate_img:MatLike = apply_truncate_filter(img)
    
    blurred = cv2.GaussianBlur(truncate_img, (5, 5), 0)

    thresh = cv2.adaptiveThreshold(
        truncate_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh


