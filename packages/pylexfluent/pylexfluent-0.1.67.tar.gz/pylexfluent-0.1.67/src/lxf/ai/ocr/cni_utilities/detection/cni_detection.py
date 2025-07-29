import os
import logging
from typing import List, Tuple

from lxf.settings import get_logging_level

logger = logging.getLogger('cni detection')
fh = logging.FileHandler('./logs/cni_detection.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)

import cv2
from cv2.typing import MatLike , RotatedRect
import numpy as np
import lxf.ai.ocr.cni_utilities.detection.rois as rois
from lxf.domain.cni_zones import CniDetectedZone, CniZones
from lxf.services.measure_time import measure_time


@measure_time
def detection(filename:str)->CniDetectedZone:
    """
    Pipeline complet pour détecter les informations dans une image de CNI.
    filename: chemin de l'image
    return: instance de CniDetectedZone avec les résultats

    """
    img:MatLike = rois.load_and_prepare_image(filename)
    rect :RotatedRect= rois.detect_main_contours(img)
    cni = rois.extract_cni(img, rect)
    rect = rois.detect_main_contours(cni)
    rotated_img :MatLike= rois.rotate_image(cni, rect)
    TARGET_WIDTH = 1040
    TARGET_HEIGHT = 740
    adjusted_img = cv2.resize(rotated_img, (TARGET_WIDTH, TARGET_HEIGHT))
    adjusted_img, x, y, w, h = rois.detect_and_adjust_blue_zone(adjusted_img)
    recto: bool= rois.check_recto_verso(adjusted_img)

    #save_image(adjusted_img, "data/assets/rotated_images", os.path.basename(filename).replace('.jpg', '_rotated.jpg'))

    result:CniDetectedZone = CniDetectedZone()
    result.is_recto = recto
    result.image = adjusted_img
    result.y = y
    result.hauteur =h
    result.x=x
    result.largeur=w
    return result



@measure_time
def detectFront(detectedZone:CniDetectedZone )->CniZones :
        """
        Détecter les zones du devant d'une cni 
        Retourne les zones :
        - La photo
        - Identification
        - Information
        - MRZ
        """
        if detectedZone==None or detectedZone.image.any==False:
             logger.error(f"Paramètre zone incorrecte!({detectedZone})")
             return None 
        y_blue= detectedZone.y
        adjusted_img=detectedZone.image
        h_blue=detectedZone.hauteur
        x_blue=detectedZone.x
        w_blue=detectedZone.largeur

        h_img, w_img, _ = adjusted_img.shape

        # Zone ID : directement sous la zone bleue
        x_id = x_blue
        y_id = y_blue + h_blue -10 
        w_id = w_blue
        h_id = h_blue
        roi_id = adjusted_img[y_id:y_id + h_id, x_id:x_id + w_id]

        offset_x_info = int(w_id * 0.29)  
        x_info = x_id + offset_x_info  
        y_info = y_id + h_id  
        w_info = w_id - offset_x_info  
        h_info = int(2.1 * h_id)+1
        roi_info = adjusted_img[y_info:y_info + h_info, x_info:x_info + w_info]

        x_date = x_info  
        y_date = y_info + h_info  
        w_date = w_info
        h_date = int(h_info /1)
        roi_date_naissance = adjusted_img[y_date:y_date + h_date, x_date:x_date + w_date]

        w_photo = int(w_id -w_info) 
        h_photo = h_id +300  
        x_photo = max(0, x_id - w_photo - 1500)  
        y_photo = y_id +h_id 
        roi_photo = adjusted_img[y_photo:y_photo + h_photo, x_photo:x_photo + w_photo]

        x_mrz = x_blue
        h_mrz = int(3.5 * h_id)
        y_mrz = h_img - h_mrz  
        w_mrz = w_blue
        roi_mrz = adjusted_img[y_mrz:y_mrz + h_mrz, x_mrz:x_mrz + w_mrz]


        zones=CniZones()
        zones.photo= roi_photo
        zones.id= roi_id
        zones.info= roi_info
        zones.mrz = roi_mrz
        zones.dat_of_birth=roi_date_naissance
        return zones 


@measure_time
def detectBack (image:MatLike)->MatLike:
        """
        Paramètre: l'image verso de la CNI. 
        Retourne: Informations contenues au verso de la cni.
        """
        if image is None or image.size == 0:
            raise Exception(f"L'image source {image} est vide ou non initialisée.")
  
        h, w, _ = image.shape
        half_h = h // 2
        verso = image[half_h - 125:half_h + 28, :]

        return verso