
import logging

from lxf.settings import get_logging_level

logger = logging.getLogger('Text extractor')
fh = logging.FileHandler('./logs/text_extractor.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)

from typing import List, Optional, Tuple

from lxf.services.measure_time import measure_time
import pytesseract
import cv2
from cv2.typing import MatLike
import easyocr


reader = easyocr.Reader(['fr'],gpu=True) 
if reader==None :
    msg ="Obtention impossible d'un easyocr reader"
    print(msg)
    logger.error(msg)
else :
    msg="Easyocr reader pret"
    print(msg)
    logger.info(msg)
cpu_reader = easyocr.Reader(['fr'],gpu=False)
if cpu_reader==None : 
    msg ="Obtention impossible d'un CPU easyocr reader"
    print(msg)
    logger.error(msg)
else :
    msg="CPU Easyocr reader pret"
    print(msg)
    logger.info(msg)    
    
@measure_time
def extract_text_from_image(final: MatLike, use_tesseract: bool = True,use_GPU:bool=True) -> str:
    """
    Extrait le texte d'une image en utilisant EasyOCR ou Tesseract.
    """
            # Telesserac config
        # Add -l LANG[+LANG] to the command line to use multiple languages together for recognition
        #     -l eng+deu
        # quiet to suppress messages
        # pdf This creates a pdf with the image and a separate searchable text layer with the recognized text.
        # Use --oem 1 for LSTM/neural network, --oem 0 for Legacy Tesseract.
        # –psm 3 - Fully automatic page segmentation, but no OSD. (Default)
        # –psm 6 - Assume a single uniform block of text.
        # –psm 11  Use pdftotext for preserving layout for text output
        # Use -c preserve_interword_spaces=1 to preserve spaces
        # hocr to get the HOCR output
        # <?xml version="1.0" encoding="UTF-8"?>
        # <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        #     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        # <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        #  <head>
        #   <title></title>
        #   <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
        #   <meta name='ocr-system' content='tesseract 5.0.1-64-g3c22' />
        #   <meta name='ocr-capabilities' content='ocr_page ocr_carea ocr_par ocr_line ocrx_word ocrp_wconf'/>
        #  </head>
        #  <body>
        #   <div class='ocr_page' id='page_1' title='image "images/eurotext.png"; bbox 0 0 640 500; ppageno 0; scan_res 300 300'>
        #    <div class='ocr_carea' id='block_1_1' title="bbox 61 41 574 413">
        #     <p class='ocr_par' id='par_1_1' lang='eng' title="bbox 61 41 574 413">
        #      <span class='ocr_line' id='line_1_1' title="bbox 65 41 515 71; baseline 0.013 -11; x_size 25; x_descenders 5; x_ascenders 6">
        #       <span class='ocrx_word' id='word_1_1' title='bbox 65 41 111 61; x_wconf 96'>The</span>
        #       <span class='ocrx_word' id='word_1_2' title='bbox 128 42 217 66; x_wconf 95'>(quick)</span>
        #       <span class='ocrx_word' id='word_1_3' title='bbox 235 43 330 68; x_wconf 95'>[brown]</span>
        #       <span class='ocrx_word' id='word_1_4' title='bbox 349 44 415 69; x_wconf 94'>{fox}</span>
        #       <span class='ocrx_word' id='word_1_5' title='bbox 429 45 515 71; x_wconf 96'>jumps!</span>
        #      </span>

        # ...

        #      <span class='ocr_line' id='line_1_12' title="bbox 61 385 444 413; baseline 0.013 -9; x_size 24; x_descenders 4; x_ascenders 5">
        #       <span class='ocrx_word' id='word_1_62' title='bbox 61 385 119 405; x_wconf 92'>salta</span>
        #       <span class='ocrx_word' id='word_1_63' title='bbox 135 385 200 406; x_wconf 92'>sobre</span>
        #       <span class='ocrx_word' id='word_1_64' title='bbox 216 392 229 406; x_wconf 83'>o</span>
        #       <span class='ocrx_word' id='word_1_65' title='bbox 244 388 285 407; x_wconf 80'>cdo</span>
        #       <span class='ocrx_word' id='word_1_66' title='bbox 300 388 444 413; x_wconf 92'>preguigoso.</span>
        #      </span>
        #     </p>
        #    </div>
        #   </div>
        #  </body>
        # </html>
        # TSV to get the TSV output :
        # level   page_num        block_num       par_num line_num        word_num        left    top     width   height  conf    text
        # 1       1       0       0       0       0       0       0       640     500     -1
        # 2       1       1       0       0       0       61      41      513     372     -1
        # 3       1       1       1       0       0       61      41      513     372     -1
        # 4       1       1       1       1       0       65      41      450     30      -1
        # 5       1       1       1       1       1       65      41      46      20      96.063751       The
        # 5       1       1       1       1       2       128     42      89      24      95.965691       (quick)
        # 5       1       1       1       1       3       235     43      95      25      95.835831       [brown]
        # 5       1       1       1       1       4       349     44      66      25      94.899742       {fox}
        # 5       1       1       1       1       5       429     45      86      26      96.683357       jumps!
    custom_config = r'--oem 1 --oem 3 --psm 6 '        

    if use_tesseract :
         text=pytesseract.image_to_string(final,lang="fra",config=custom_config)

    else:
        try:
            text = ""
            if use_GPU :
                result = reader.readtext(final, detail=0)
            else : 
                result = cpu_reader.readtext(final,detail=0)
            text = " ".join(result)
        except Exception as ex:
            logger.error(f"Exception pendant l'extraction de texte : {ex}. \nEssai en CPU")
            return extract_text_from_image(final,use_tesseract=False,use_GPU=False)
    return text