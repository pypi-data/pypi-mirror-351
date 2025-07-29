import glob
import logging
import os
import shutil

from lxf import settings
#logger
logger = logging.getLogger('OCR')
fh = logging.FileHandler('./logs/iban_ocr.log')
fh.setLevel(settings.get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(settings.get_logging_level())
logger.addHandler(fh)


import re
from typing import List
import cv2

from pdf2image import convert_from_path, convert_from_bytes
from pathlib import Path

from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
import numpy as np
from tqdm import tqdm

from lxf.services.measure_time import measure_time, measure_time_async
from lxf.ai.ocr.text_extractor import extract_text_from_image





def check_path() ->None:
    """
    """
    data_path =Path("./data")
    if not data_path.exists: data_path.mkdir()
    image_path=Path("./data/images")    
    if not image_path.exists(): image_path.mkdir()
    temp_path=Path("./data/images/temp")
    if not temp_path.exists() : temp_path.mkdir()
    temp_document_path=Path("./data/temp-document")
    if not temp_document_path.exists() : temp_document_path.mkdir()
    temp_document_images_path = Path("./data/temp-document/images")
    if not temp_document_images_path.exists(): temp_document_images_path.mkdir()

# Credits to https://becominghuman.ai/how-to-automatically-deskew-straighten-a-text-image-using-opencv-a0c30aed83df
def getSkewAngle(cvImage) -> float:
    check_path()
    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()
    
    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)

    thresh, img_bw = cv2.threshold(gray,150,250,cv2.THRESH_BINARY)
    #cv2.imwrite("./data/images//temp/deskew_img_bw.png", img_bw)

    no_noise = noise_removal(img_bw)
    #cv2.imwrite("./data/images/temp/deskwe_no_noise.jpg", no_noise)

    blur = cv2.GaussianBlur(no_noise, (9, 9), 0)
    #cv2.imwrite("./data/images/temp/deskew_blur.jpg",blur)    

    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    #cv2.imwrite("./data/images/temp/deskew_thresh.jpg",thresh)
    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 9))
    dilate = cv2.dilate(thresh, kernel, iterations=1)
    #cv2.imwrite("./data/images/temp/deskew_dilate.jpg",dilate)
    
    # Find all contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours)==0 : return 0.0 
    contours = sorted(contours, key = cv2.contourArea, reverse = True)    
    for c in contours:
        rect = cv2.boundingRect(c)
        x,y,w,h = rect
        cv2.rectangle(newImage,(x,y),(x+w,y+h),(0,255,0),2)

    # Find largest contour and surround in min area box
    largestContour = contours[0]
    #logger.debug (len(contours))
    minAreaRect = cv2.minAreaRect(largestContour)
    box = np.intp(cv2.boxPoints(minAreaRect))
    cv2.drawContours(newImage, [box], 0, (0,0,255), 3)
    #cv2.imwrite("./data/images/temp/boxes.jpg", newImage)
    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    #logger.debug(f"Deskew angle:{angle}")
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle

# Deskew image
def deskew(cvImage,correction_angle:float=1):
    angle = getSkewAngle(cvImage)
    logger.debug(f"Angle a corriger {angle}")
    if (abs(angle)<3):
        if angle>0 :
            correction_angle=-correction_angle
        else :
            correction_angle=correction_angle
        logger.debug(f"Facteur de correction d'angle retenue {correction_angle}")
        angle= correction_angle * angle
        logger.debug(f"Angle finale retenue {angle}")
        logger.debug("Rotation")
        return rotateImage(cvImage,angle )
    else :
        return cvImage
    
# Rotate the image around its center
def rotateImage(cvImage, angle: float):
    newImage = cvImage.copy()
    (h, w) = newImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage

def to_gray(image):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    return gray

def noise_removal(image):
    import numpy as np
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.medianBlur(image, 3)
    return (image)

def thin_font(image):
    import numpy as np
    image = cv2.bitwise_not(image)
    kernel = np.ones((2,2),np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.bitwise_not(image)
    return (image)

def remove_borders(image):
    contours, hiearchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cntsSorted = sorted(contours, key=lambda x:cv2.contourArea(x))
    cnt = cntsSorted[-1]
    x, y, w, h = cv2.boundingRect(cnt)
    crop = image[y:y+h, x:x+w]
    return (crop)

def sortKeyColunm(x, hmax,hmoy,wmoy):
    x,y,w,h = cv2.boundingRect(x)
    col = x//wmoy
    line = y//hmoy
    return x+col*hmax+line*hmoy

def sortKeyRow(x,xmax,href,wref) :
    x,y,w,h = cv2.boundingRect(x)
    nb_cols=max(xmax//wref,1)
    col = max(x//wref,1)
    line = max(y//href,1)
    return line*nb_cols+col

def detect_struct(image,
                  max_high:float=1900.0,
                  min_high:float=80.0,
                  max_wide:float=1500.00,
                  min_wide:float=60.00,
                  intermediate_files:bool=False,
                  threshold_min:float=150.00,
                  threshold_max:float=255.00,
                  filter:bool=True,
                  max_box:bool=False,
                  hmoy_filter_correction:float=0.5,
                  wmoy_filter_correction:float=0.5,
                  kernel_dilated_size:any=(10,10),
                  kernel_blur_size:any=(17,19), 
                  column_direction:bool=False):
    """
    Compute the ROI of the image 
    """
    check_path()
    # Deskew
    image = deskew(image,correction_angle=0.8)
    # convert to gray
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    if intermediate_files : cv2.imwrite("./data/images/temp/gray.png",gray)
    thresh, img_bw = cv2.threshold(gray,threshold_min,threshold_max,cv2.THRESH_BINARY)
    if intermediate_files : cv2.imwrite("./data/images/temp/img_bw.png", img_bw)
    #no_noise = noise_removal(gray)
    #cv2.imwrite("./data/images/temp/no_noise.jpg", no_noise)
    # blur
    blur = cv2.GaussianBlur(img_bw,kernel_blur_size,0)
    if intermediate_files : cv2.imwrite ("./data/images/temp/blur_0.png",blur)
    # threshold 
    #thresh=cv2.threshold(no_noise,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    thresh=cv2.threshold(blur,threshold_min,threshold_max,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    if intermediate_files : cv2.imwrite("./data/images/temp/thresh_0.png",thresh)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,kernel_dilated_size)
    if intermediate_files : cv2.imwrite("./data/images/temp/kernel.png",kernel)
    dilate = cv2.dilate(thresh, kernel, iterations=1)
    if intermediate_files : cv2.imwrite("./data/images/temp/dilate_0.png",dilate)
    cnts = cv2.findContours(dilate,cv2.RETR_LIST,cv2.CHAIN_APPROX_TC89_KCOS)
    cnts = cnts[0] if len(cnts)==2 else cnts[1]
    ymax=0.0
    xmax=0.0
    xmin=10000000.0
    ymin=10000000.0
    hmin=10000000.0
    wmax=0.0
    wmin=10000000.0
    hmax=0.0
    wmoy=0.0
    hmoy=0.0
    
    n=len(cnts)
    for cnt in cnts:
        x,y,w,h =cv2.boundingRect(cnt)
        if y>ymax : ymax=y
        if x>xmax : xmax=x
        if x<xmin : xmin=x
        if y<ymin : ymin=y
        if w>wmax : wmax=w
        if w<wmin : wmin=w
        if h>hmax : hmax=h
        if h<hmin : hmin=h
        wmoy+=w/n
        hmoy+=h/n
    if intermediate_files : logger.debug(f"h Max={ymax} h moyen = {hmoy} w moyen = {wmoy}")
    # trier les ROIS en fonction du mode de direction choisi 
    if column_direction :
        cnts = sorted(cnts,key=lambda x: sortKeyColunm(x,ymax,hmoy,wmoy),reverse=True)
    else :
        cnts = sorted(cnts,key=lambda x: sortKeyRow(x,xmax,hmin,wmin),reverse=True)
    rois=[]
    base_image = image.copy()  
    lg=len(cnts)  
    if max_box:
            # We take only the greatest bounding rectangle
            roi = base_image[ymin:ymin+hmax,xmin:xmin+wmax]
            rois.append(roi)
            cv2.rectangle(image,(xmin,ymin),(xmin+wmax,ymin+hmax),(0,255,0),2)        
    else:
        for i in range(lg) :
            c=cnts[lg-i-1]
            x,y,w,h = cv2.boundingRect(c)
            
            if (filter==True) :
                # We filter by max_high and maw_wide
                if h <=max_high and h >=min_high :
                    if (h>hmoy_filter_correction*hmoy and h<max_high) and (w>wmoy_filter_correction*wmoy and w<max_wide):
                        roi = base_image[y:y+h,x:x+w]
                        rois.append(roi)     
                        cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
            else :
                # We take all 
                roi = base_image[y:y+h,x:x+w]
                rois.append(roi)
                cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)

            
    if intermediate_files : 
        cv2.imwrite("./data/images/temp/bbox.png",image)
        i=0
        for roi in rois:
            i+=1
            cv2.imwrite(f"./data/images/temp/rois_{i}.png",roi)
    return rois

def sanitize_text(text:str)->str:
    regex=r"\n"
    subst=" "
    result = re.sub(regex, subst, text, 0, re.MULTILINE)
    regex=r" {2,}"
    result = re.sub(regex, subst, result, 0, re.MULTILINE)
    regex=r"\. "
    subst=".\n"
    result = re.sub(regex, subst, result, 0, re.MULTILINE)
    return result

@measure_time
def recognize_rois(text:List[str],rois,intermediate_files:bool, sanitize:bool, threshold_limit:float=150)->List[str]:
    check_path()
    text=[]
   
    for i,image_roi in tqdm(enumerate(rois),desc="Analyse des ROI ",disable=not settings.enable_tqdm):
        img_gray = to_gray(image_roi)
        if intermediate_files : 
            cv2.imwrite(f"./data/images/temp/rois_{i+1}_ngray.jpg",img_gray)
        thresh, img_bw = cv2.threshold(img_gray,threshold_limit,255,cv2.THRESH_TRUNC)
        if intermediate_files : 
            cv2.imwrite(f"./data/images//temp/rois_{i+1}_bw.png", img_bw)
        img_nonoise = noise_removal(img_bw)
        if intermediate_files : 
            cv2.imwrite(f"./data/images/temp/rois_{i+1}_no_noise.jpg",img_nonoise)
        img = img_bw
        txt = extract_text_from_image(img)
        if txt!=None and txt!="":
            text.append(txt)


    return text

@measure_time_async
async def do_OcrImage_from_pdf(path_filename:str,
                               intermediate_files:bool=False,
                               rois_filter:bool=True, 
                               threshold_limit:float=180,
                               threshold_limit_recognize:float=200,
                               threshold_max:float=225,
                               hmoy_filter_correction=0.05,
                               wmoy_filter_correction=0.05,
                               sanitize:bool=True,
                               min_high:float=25,
                               min_wide:float=50,
                               kernel_dilated_size=(19,5),
                               kernel_blur_size=(17,9)
                               )->list[str]:
    """
    Effectue une détection par traitement image du pdf suivi d'une reconnaissance OCR 
    Retourne une lists de texte reconnu pour chaque zone (ROI) 
    """

    check_path()
    document_path = Path('./data/temp-document/images')
    pages = convert_from_path(path_filename)
    texts=""
    text_rois=[]
    pages_reconnues:list[list[str]]=[]
    for i in tqdm(range(len(pages)),desc="Analyse des pages ",disable=not settings.enable_tqdm):
        ## Save image to file
        pages[i].save(f"{document_path}/page_{i}.jpeg",'JPEG')
        page = cv2.imread(f"{document_path}/page_{i}.jpeg")    
        
        #detection
        rois = detect_struct(page,
                             filter=rois_filter, 
                             threshold_min=threshold_limit,
                             threshold_max=threshold_max,
                             hmoy_filter_correction=hmoy_filter_correction,
                             wmoy_filter_correction=wmoy_filter_correction,
                             min_high=min_high,
                             min_wide=min_wide,
                             kernel_dilated_size=kernel_dilated_size,
                             kernel_blur_size=kernel_blur_size
                             )
        # recognition
        text_rois=recognize_rois(text_rois,rois,intermediate_files,sanitize, threshold_limit=threshold_limit_recognize)
        pages_reconnues.append(text_rois)
    # Supprimer tous les fichiers images (mais pas les sous-dossiers)
    fichiers = glob.glob(os.path.join(document_path, '*'))
    for f in fichiers:
        if os.path.isfile(f):
            os.remove(f)        
    return pages_reconnues

@measure_time_async
async def do_IBAN_Ocr_from_pdf(path_filename:str,intermediate_files:bool=False,rois_filter:bool=True, threshold_limit:float=180,sanitize:bool=True):

    check_path()
    document_path = Path('./data/temp-document/images')
    pages = convert_from_path(path_filename)
    texts=""
    text_rois=[]
    for i in tqdm(range(len(pages)),desc="Analyse des pages ",disable=not settings.enable_tqdm):
        ## Save image to file
        pages[i].save(f"{document_path}/page_{i}.jpeg",'JPEG')
        page = cv2.imread(f"{document_path}/page_{i}.jpeg")    
        
        #detection
        rois = detect_struct(page,
                             filter=rois_filter, 
                             threshold_min=threshold_limit,
                             hmoy_filter_correction=0.05,
                             wmoy_filter_correction=0.05,
                             min_high=50,
                             min_wide=50,
                             kernel_dilated_size=(19,7),
                             kernel_blur_size=(17,9)
                             )
        # recognition
        text_rois=recognize_rois(text_rois,rois,intermediate_files,sanitize, threshold_limit=threshold_limit)
        if text_rois != None : temp = " ".join(text_rois)
        if sanitize : 
            texts += sanitize_text(temp)
    return texts

async def do_IBAN_Ocr_from_image(path_filename:str,intermediate_files:bool=False, rois_filter:bool=True, threshold_limit:float=180, sanitize:bool=True):

    check_path()
    text=[]
    page = cv2.imread(path_filename.__str__())        
    #detection
    rois = detect_struct(page,filter=rois_filter, threshold_min=threshold_limit)
    # recognition
    text=recognize_rois(text,rois,intermediate_files,sanitize, threshold_limit=threshold_limit)
    texts=""
    if text != None : texts = " ".join(text)
    if sanitize : 
        texts = sanitize_text(texts)
    return texts    

