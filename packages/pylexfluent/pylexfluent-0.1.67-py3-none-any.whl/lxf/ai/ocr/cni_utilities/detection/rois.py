import logging
from typing import Tuple
from lxf.settings import get_logging_level
import mediapipe as mp

#logger
logger = logging.getLogger('rois cni')
fh = logging.FileHandler('./logs/cni_rois.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)

import cv2
from cv2.typing import MatLike , RotatedRect
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
import numpy as np
import re
import os
import locale
from enum import IntEnum


# Credits to https://becominghuman.ai/how-to-automatically-deskew-straighten-a-text-image-using-opencv-a0c30aed83df
def getSkewAngle(cvImage) -> float:
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
    contours = sorted(contours, key = cv2.contourArea, reverse = True)
    for c in contours:
        rect = cv2.boundingRect(c)
        x,y,w,h = rect
        cv2.rectangle(newImage,(x,y),(x+w,y+h),(0,255,0),2)

    # Find largest contour and surround in min area box
    largestContour = contours[0]
    #print (len(contours))
    minAreaRect = cv2.minAreaRect(largestContour)
    box = np.intp(cv2.boxPoints(minAreaRect))
    cv2.drawContours(newImage, [box], 0, (0,0,255), 3)
    #cv2.imwrite("./data/images/temp/boxes.jpg", newImage)
    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    #print(f"Deskew angle:{angle}")
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle



def correct_orientation(cvImage : MatLike, rect: RotatedRect)->MatLike:
    # Calculate the angle from rect
    angle : float= rect[2]
    if rect[1][0] < rect[1][1]:
        angle = 90 - rect[2]
    else:
        angle = rect[2]
    
    center_rect = rect[0]
    (h1, w1) = cvImage.shape[:2]
    M : MatLike = cv2.getRotationMatrix2D(center_rect, angle, 1.0)
    cos:float = np.abs(M[0, 0])
    sin:float = np.abs(M[0, 1])
    new_w:int = int((w1 * cos) + (h1 * sin))
    new_h:int = int((h1 * cos) + (w1 * sin))
    M[0, 2] += (new_w / 2) - center_rect[0]
    M[1, 2] += (new_h / 2) - center_rect[1]
    deskewed_image:MatLike = cv2.warpAffine(cvImage, M, (new_w, new_h))
    
    return deskewed_image
    
# Rotate the image around its center
def rotateImage(cvImage, angle:float):
    """
    Effectue une rotation de l'image autour de son centre.
    """
    (h, w) = cvImage.shape[:2]
    center = (w // 2, h // 2)
    # Créer la matrice de rotation
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    # Appliquer la transformation affine
    rotated = cv2.warpAffine(cvImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

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
    kernel = np.ones((1,1),np.uint8)
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

def sortKeyByColumns(x, hmax,hmoy,wmoy):    
    x,y,w,h = cv2.boundingRect(x)
    col = x//wmoy
    line = y//hmoy
    return x+col*hmax+line*hmoy

def sortKeyByRows(x, hmax,hmoy,wmoy):
    x,y,w,h = cv2.boundingRect(x)
    col = x//wmoy
    line = y//hmoy
    return x+col*wmoy+line*hmoy


class ReadRirection(IntEnum):
    row=0
    col=1

def detect_struct(image, name:str="X",
                  max_high:float=1900.0,
                  min_high:float=80.0,
                  max_wide:float=1500.00,
                  min_wide:float=60.00,
                  direction:ReadRirection=ReadRirection.row,
                  displayIntermediare:bool=False) :
    
    """
    Compute the ROI of the image 
    """
    
    # convert to gray
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(17,19),0)
    
    thresh=cv2.threshold(blur,150,250,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
 
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(21,21))
   
    dilate = cv2.dilate(thresh, kernel, iterations=1)

    cv2.imwrite("./ocr/detection/data/images/temp/dilate.jpg",dilate)

    cnts = cv2.findContours(dilate,cv2.RETR_LIST,cv2.CHAIN_APPROX_TC89_KCOS)
    cnts = cnts[0] if len(cnts)==2 else cnts[1]
    ymax=0.0
    wmoy=0.0
    hmoy=0.0
    
    n=len(cnts)
    for cnt in cnts:
        x,y,w,h =cv2.boundingRect(cnt)
        if y>ymax : ymax=y
        wmoy+=w/n
        hmoy+=h/n

    if direction==ReadRirection.col :
        cnts = sorted(cnts,key=lambda x: sortKeyByColumns(x,ymax,hmoy,wmoy),reverse=True)
    if direction==ReadRirection.row:
        cnts = sorted(cnts,key=lambda x: sortKeyByRows(x,ymax,hmoy,wmoy),reverse=True)


    rois=[]
    base_image = image.copy()
    lg=len(cnts)
    for i in range(lg) :
        c=cnts[lg-i-1]
        x,y,w,h = cv2.boundingRect(c)
        if (h>0.5*hmoy and h<max_high) and (w>0.5*wmoy and w<max_wide):
            roi = base_image[y:y+h,x:x+w]
            rois.append(roi)     
            cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)

    for roi in rois:
        i+=1
        cv2.imwrite(f"./ocr/detection/data/images/temp/rois_{i}.png",roi)
            
    cv2.imwrite(f"./ocr/detection/data/images/temp/bbox_{name}.png",image)
    
    return rois



def smooth(img, type="mean", kernel_size=9):
    if type == "mean":
        return cv2.blur(img, (kernel_size, kernel_size))
    elif type == "median":
        return cv2.medianBlur(img, kernel_size)
    elif type == "gaussian":
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    else:
        raise Exception(f"Unsupported smoothing type: {type}")



def get_limits(color=[255,0,0])->Tuple[np.ndarray, np.ndarray]:
    """
    Calcule les limites inférieure et supérieure HSV pour une couleur donnée en BGR.
    """
    c :np.ndarray = np.uint8([[color]])  
    hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)

    lowerLimit:Tuple[int, int, int] = hsvC[0][0][0] - 15, 50, 50
    upperLimit:Tuple[int, int, int]  = hsvC[0][0][0] + 15, 255, 255

    lowerLimit = np.array(lowerLimit, dtype=np.uint8)
    upperLimit = np.array(upperLimit, dtype=np.uint8)

    return lowerLimit, upperLimit

def save_image(image: MatLike, folder: str, filename: str) -> None:
    """
    Sauvegarde une image dans un dossier spécifié.
    image: Image à sauvegarder au format MatLike.
    folder: Chemin du dossier de sauvegarde.
    filename: Nom du fichier.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    output_path: str = os.path.join(folder, filename)
    cv2.imwrite(output_path, image)
    logger.debug(f"Image sauvegardée dans : {output_path}")

def load_and_prepare_image(filename:str)->MatLike:
    """
    filename: chemin du fichier image.
    return: image chargée
    """
    if not os.path.exists(filename):
        raise Exception(f"Le fichier {filename} n'existe pas")
    img = cv2.imread(filename)
    return img

def detect_main_contours(img:MatLike)-> RotatedRect:
    """
    Détecte le contour principal dans une image.
    img : image source.
    return: rectangle correspondant au contour principal.

    """
    gray:MatLike = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    blur:MatLike = cv2.GaussianBlur(gray, (5, 5), 0)
    
    canny:MatLike = cv2.Canny(blur, 10, 70)
    
    thresh:MatLike = cv2.adaptiveThreshold(canny, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 17, 2)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt = max(contours, key=cv2.contourArea)
    
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    return rect

def rotate_image(img:MatLike, rect)->MatLike:
    """
    Effectue la rotation d'une image selon un rectangle détécté.
    img: image source.
    rect: rectangle rotatif détecté.
    return: image après rotation.
    """
    center:Tuple[float,float] = rect[0]
    angle:float = rect[2]
    if rect[1][0] < rect[1][1]:
        angle = 90 - rect[2]
    else:
        angle = rect[2]
    
    M:MatLike = cv2.getRotationMatrix2D(center, angle, 1.0)
    (h, w) = img.shape[:2]
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((w * cos) + (h * sin))
    new_h = int((h * cos) + (w * sin))
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]
    
    rotated_img:MatLike = cv2.warpAffine(img, M, (new_w, new_h))
    return rotated_img

def detect_and_adjust_blue_zone(img:MatLike)->Tuple[MatLike, int, int, int, int]:
    """
        Détecte et ajuste la zone bleue dans une image.
        img : image source.
        retrun : image ajustée et coordonnées (x, y, w, h) de la zone bleue.
    """
    hsv:MatLike = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # lower_blue = np.array([100, 50, 50])  
    # upper_blue = np.array([140, 255, 255]) 
    lower_blue, upper_blue=get_limits()
    mask: MatLike= cv2.inRange(hsv, lower_blue, upper_blue)
    
    kernel = np.ones((5, 5), np.uint8)
    mask:MatLike = cv2.erode(mask, kernel, iterations=1)
    mask:MatLike = cv2.dilate(mask, kernel, iterations=1)
    mask:MatLike= cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt :MatLike= max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(cnt)
    
    if y > img.shape[0] / 2:  # Si la zone bleue est en bas
        img = cv2.rotate(img, cv2.ROTATE_180)
        
        # Recalculer les coordonnées après la rotation
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnt = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(cnt)

    return img, x, y, w, h



# def check_recto_verso(img:MatLike)->bool:
#     """
#     Vérifie si une image est en recto (avec visage) ou verso
#     img: image cni
#     return: True si recto, sinon False
#     """
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
#     gray:MatLike = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
#     recto = len(faces) > 0

#     return recto

def check_recto_verso(img: MatLike) -> bool:
    """
    Vérifie si une image cni est en recto (avec visage) ou verso.
    img: image source
    return: True si recto, sinon False
    """
    mp_face_detection = mp.solutions.face_detection
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        results = face_detection.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        recto = results.detections is not None
    return recto


def extract_cni(img : MatLike, rect:RotatedRect)->MatLike:
    """
    Extrait la région de la CNI 
    img:Image source
    return: la cni detectée 
    
    """
    box:np.ndarray = cv2.boxPoints(rect)
    box = np.int0(box)
    x, y, w, h = cv2.boundingRect(box)
    # Découper la région d'intérêt 
    cni = img[y:y + h, x:x + w]
    return cni