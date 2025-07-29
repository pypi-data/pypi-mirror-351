# Logging stuff
import logging
from multiprocessing import Process, Queue
import lxf.settings as settings 


logger = logging.getLogger('Iban Analyzer')
fh = logging.FileHandler('./logs/iban_analyzer.log')
fh.setLevel(settings.get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(settings.get_logging_level())
logger.addHandler(fh)
#####################
from tqdm import tqdm
import datetime
from xml.dom import ValidationErr
from lxf.domain.iban import IbanCandidate, Iban

from typing import List
import re 
import requests
import json
from spacy.language import Language


 
APIkey = "3b63fb5dbf988c046786c779ff6cc0bf"
uri = 'https://api.iban.com/clients/api/v4/iban/'
 
lazy_loading = None
IBAN_ENTITY = "IBAN" 
IBAN_ENTITY_TILTE ="IBAN_TITLE"
IBAN_SIGLE="IBAN_SIGLE"

def get_nlp():
    return settings.load_model()

def sanitize_blank(text:str)->str:
    regex = r"  +"
    subst = " "
    # You can manually specify the number of replacements by changing the 4th argument
    temp = re.sub(regex, subst, text, 0, re.MULTILINE)
    regex =r"\n{2}"
    subst="\n"
    result =re.sub(regex, subst, temp, 0, re.MULTILINE)
    return result 

 
class IbanAnalyzer :
    def __init__(self, text:str, nlp:Language=None) :
        self.text=sanitize_blank(text)
        if nlp==None:
            self.nlp = get_nlp()
        else :
            self.nlp= nlp

    def do_analyze(self)->List[IbanCandidate] :
        doc= self.nlp(self.text)
        ibans=[]
        for ent in doc.ents: 
            if ent.label_==IBAN_ENTITY :
                iban:Iban = Iban()
                iban.text = ent.text
                ibans.append(iban)
        return self.check_ibans(ibans)   
    
    def check_validations_helper(self,response) -> tuple[bool,str]:
        """
        """
        queue=Queue()
        p=Process(target=self.check_validations, args=(response,queue))
        p.start()
        p.join()
        result:dict[bool,str]= queue.get(True)
        if result!=None :
            return result.get("validation"), result.get("error_msg")
        else: 
            logger.error("Aucune validation effectuee depuis IBAN.com")
            return False,"Aucune validation effectuee depuis IBAN.com"



    #Check if iban.com returned a valid Iban
    def check_validations(self, response,queue:Queue):
        code = response.get('validations')['iban'].get('code')
        error_msg=response.get('validations')['iban'].get('message')
        validation= response.get('validations')["iban"].get('code').startswith('00')
        if not validation : 
            error_msg= f"{datetime.datetime.today().strftime('%d/%m/%Y %H:%M')}: IBAN.COM retourne l'erreur {code} => {error_msg}"
        else :
            error_msg=f"{datetime.datetime.today().strftime('%d/%m/%Y %H:%M')}: IBAN.COM retourne le code de validation {code} => {error_msg}"
        queue.put({"validation":validation,"error_msg":error_msg},True)
        

    #Main method to check the text
    async def check_ibans(self, ibans_found :List[Iban])->List[IbanCandidate]:
        """
        """
        candidate_list:List[IbanCandidate] = []
        if len(ibans_found) > 0:
            for iban in tqdm(ibans_found,desc="Analyse des IBAN trouvés ",disable=not settings.enable_tqdm):
                #Call iban.com API
                response = requests.post(uri, {'format':'json', 'api_key': APIkey,'iban': iban.text})
                res_json = json.loads(response.text, strict=False)
                #Check if iban if valid                     
                      
                validation, error_msg = self.check_validations_helper(res_json)
                #Try to dump returned informations 
                if 'bank_data' in res_json and res_json.get('bank_data') != None:
                    bank = res_json.get('bank_data')
                    try:
                        candidate = IbanCandidate(**bank)
                    except ValidationErr as e:
                        logger.error(f"An exception occured when constructing IbanCandidate class for {iban.text} : {e.json()}")
                        continue
                    candidate.iban = iban.text
                    candidate.found = "Yes"
                    candidate.validation = validation
                    candidate.error_msg=error_msg
                    candidate_list.append(candidate)
                else:
                    candidate = IbanCandidate({"iban": iban.text, "found": None})
                    candidate_list.append(candidate)
            return candidate_list
        else:
            return []

 
