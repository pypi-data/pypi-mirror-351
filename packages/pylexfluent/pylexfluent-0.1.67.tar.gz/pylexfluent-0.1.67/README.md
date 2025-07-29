# Libraire python Lexfluent RevolutionAI

| Création/Révision | Auteur | date |
| -- | -- | --- | 
|Création | *Jacques MASSA* | 2 décembre 2024|
|Modification | *jacques MASSA* | 10 mars 2025 |

---

## Présentation

La librairie pyLexfluent propose toutes les fonctionnalités IA dans les domaines juridique et document.  

 - Classification : Entraînement et inférence
 - Extraction de données : ODP, CNI, IBAN, Document juridique, Certificat d'Urbanisme, Extrait Acte de naissance, Extrait Acte de Décés,Extrait Acte de Mariage
 - Augmentation des données : Finance

## Installations Prérequises 

``` 
pip install setuptools
pip install wheel
pip install scikit-learn
pip install matplotlib
pip install tqdm
pip install pytesseract
pip install pillow>=10.1.0
pip install jax>=0.4.38
pip install jaxlib>=0.4.38
pip install mediapipe
pip install opencv-python
pip install pandas
pip install tensorrt
pip install tensorrt-lean
pip install tensorrt-dispatch
pip install tensorflow
pip install tf-keras
pip install tensorflow-hub
pip install torch torchvision torchaudio
pip install sentence_transformers
pip install spacy[cuda12x]
pip install ocrmypdf
pip install easyocr
pip install pdf2image
pip install pdfplumber
pip install langchain-community
pip install pymongo
python -m spacy download fr_core_news_lg

```
Il y peut y avoir un conflit de version avec cuDNN requis par TensforFlow et Torch Dans ce cas il faut supprimer **nvidia-cuDNN-cu12** apporté par PIP 

```
pip uninstall nvidia-cudnn-cu12
```

 
## Téléchargement modèles 
### SPACY 

``` python -m spacy download fr_core_news_lg ```

## Update et installations requises
``` 
    apt-get update 
    apt-get upgrade
    apt install software-properties-common -y
    apt-get install poppler-utils -y
    add-apt-repository ppa:alex-p/tesseract-ocr5
    apt-get install libc6 -y
    apt-get install poppler-utils -y
    apt-get install tesseract-ocr -y
    apt-get install tesseract-ocr-fra -y
    apt-get install tesseract-ocr-eng -y
    apt-get install tesseract-ocr-ita -y
    apt-get install tesseract-ocr-spa -y
    apt-get install tesseract-ocr-deu -y
    apt-get install tesseract-ocr-cos -y
    apt-get install tesseract-ocr-lat -y
    apt-get install automake libtool -y
    apt-get install libleptonica-dev -y
    apt-get install ffmpeg libsm6 libxext6  -y
    apt-get install ocrmypdf -y    

``` 

## GPU issue 
Si problème : Successful NUMA node read from SysFS had negative value (-1) 

```
for a in /sys/bus/pci/devices/*; do echo 0 |  tee -a $a/numa_node; done

```

# Exemples d'utilisation 

## Classification  

### Code 
```
import logging
import sys

from lxf.services.measure_time import measure_time_async
from lxf.services.try_safe import try_safe_execute_asyncio



from lxf.ai.classification.classifier import get_classification
from lxf.domain.predictions import  Predictions

import lxf.settings as settings 
from lxf.settings import set_looging_level, get_logging_level
set_logging_level(logging.DEBUG)
###################################################################

logger = logging.getLogger('test classifier')
fh = logging.FileHandler('./logs/test_classifier.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)
#################################################################

@measure_time_async
async def do_test(file_name) -> Predictions :
    """
    """
    return await get_classification(file_name=file_name,max_pages=10)


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True) 
    pdf_path = "data/ODP.pdf"
    iban_pdf="data/RIBB.pdf"
    result = try_safe_execute_asyncio(logger=logger,func=do_test,file_name=iban_pdf) #asyncio.run(do_test(iban_pdf))
    print(result)    
    result = try_safe_execute_asyncio(logger=logger,func=do_test,file_name=pdf_path) #asyncio.run(do_test(pdf_path))
    print(result)

```

### Code 

```
import logging
import asyncio
import os
import sys



import lxf.settings as settings
from lxf.setting import set_logging_level, get_logging_level
set_logging_level(logging.DEBUG)
settings.enable_tqdm=False

from lxf.domain.loan import Pret
from lxf.extractors.finance import odp_extractor
from lxf.extractors.finance import iban_extractor

from lxf.services.try_safe import  try_safe_execute_async



###################################################################

logger = logging.getLogger('test_finance')
fh = logging.FileHandler('./logs/test_finance.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)
#################################################################

async def do_test_odp(file_path:str)->Pret:
    result = await try_safe_execute_async(logger,odp_extractor.extract_data,file_path=file_path)
    return result
    
async def do_test_iban(file_path:str)->str :
    """
    """
    result = await try_safe_execute_async(logger,iban_extractor.extract_data,file_path=file_path)
    return result

if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True) 
    pdf_path = "data/ODP.pdf"
    # pret:Pret=  asyncio.run(do_test_odp(file_path=pdf_path))
    # if pret!=None:
    #     print(pret.emprunteurs)
    iban_pdf="data/rib pm.pdf"
    txt = asyncio.run(do_test_iban(file_path=iban_pdf))
    print(txt)
    
```