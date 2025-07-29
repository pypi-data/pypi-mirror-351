
import logging
import os
from lxf.settings import get_logging_level

#logger
logger = logging.getLogger('OCR PDF ')
fh = logging.FileHandler('./logs/ocr_pdf.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)


import ocrmypdf

from lxf.services.measure_time import measure_time


#ocrmypdf.Verbosity(0) # Suppress most messages
#ocrmypdf.configure_logging(verbosity=0, progress_bar_friendly= False)



@measure_time
def do_ocr(input_pdf, output_pdf)->ocrmypdf.ExitCode:
    # if (maxPagesLimit>0) :
    try :    
        custom_config = r'--oem 1 --oem 3 --psm 6 ' 
        ocr_result = ocrmypdf.ocr(input_pdf,
                            output_pdf,
                            output_type='pdf',
                            skip_text=True,
                            force_ocr=False,
                            tesseract_oem=3, #Tesseract + LSTM ; 0 - original Tesseract only; 1 - neural nets  LSTM  only;  2  -Tesseract + LSTM; 3 - default
                            tesseract_pagesegmode=6, # Assume a single uniform block of text.
                            keep_temporary_files=False,
                            clean=True,language="fra+eng",
                            invalidate_digital_signatures=True,
                            use_threads=True,
                            progress_bar=False,
                            deskew=False,
                            author="Python librairie PyLexfluent",
                            keywords="OCR")
        return ocr_result
    except Exception as ex:
        logger.error(f"Exception pendant l'ocerisation de {input_pdf}")
        return ocrmypdf.ExitCode.other_error


@measure_time
def do_ocr_directory(directory_source:str,directory_dest:str):
    for root, dirs, files in os.walk(directory_source):
        if files!=[] :
            category='_'.join(root.split('/')[-3:]).replace(' ','-')
            logger.debug(f"Category: {category}")
            for f in files :  
                if '.pdf' in f:   
                    input_pdf = root+'/'+f
                    output_ocred_pdf = directory_dest+"/"+category+'#'+f 
                    # if file exists in ocr directory skip it 
                    if os.path.exists(output_ocred_pdf) == False : 
                        result = do_ocr(input_pdf,output_ocred_pdf)
                        #logger.debug(f"OCR Result for {f}: {result} ")