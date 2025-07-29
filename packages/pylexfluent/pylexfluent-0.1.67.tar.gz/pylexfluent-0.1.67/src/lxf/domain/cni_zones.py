from cv2.typing import MatLike

class CniDetectedZone :
    is_recto:bool=True
    image:MatLike=None
    y:int=0
    hauteur:int=0
    x:int=0
    largeur:int=0

class CniZones :
    photo: MatLike=None
    id : MatLike=None
    info : MatLike=None
    mrz : MatLike=None
    name: MatLike=None
    dat_of_birth: MatLike =None

