import os
import logging


from lxf.settings import get_logging_level, load_model,enable_tqdm
class CustomFormatter(logging.Formatter): 
    def format(self, record): 
        message = record.getMessage() 
        if isinstance(message, str): 
            message = message.encode('utf-8') 
            record.msg = message 
            return super().format(record)

logger = logging.getLogger('CU Extractor')
fh = logging.FileHandler('./logs/cu_extractor.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter(str('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
fh.setFormatter(formatter)
#fh.setFormatter(CustomFormatter())
logger.setLevel(get_logging_level())
logger.addHandler(fh)
#####################################################
from lxf.services.measure_time import measure_time_async
from lxf.ai.classification.classifier import extract_text_and_table_from_file
from lxf.domain.tables import lxfTable   
from lxf.utilities.text_comparator import TextComparator
from lxf.ai.text_analysis.default_text_analysis import decouper_text_par_titres
from lxf.ai.ocr.iban_ocr import do_OcrImage_from_pdf

import re



def sanitize_text(text:str) :
    """
    """
    text= text.replace('{',"").replace("}","").replace("|","").replace("«","")
    return text


def get_numero_cu(text:str)->str:
    """
    """
    regex_CU = r"CU ?[0-9]{2,3} ?[0-9]{3} ?[0-9]{2} ?[A-Za-z]?[0-9]{4,}|CU ?[0-9]?[0-9]{5} ?[0-9]{2} ?[A-Za-z]?[0-9]{4,}"
    num_cu=""
    matches = re.findall(regex_CU,text,re.MULTILINE|re.IGNORECASE)
    if matches!=None and len(matches)>0: 
        # On a trouvé un N° de CU Valide, on prend le premier trouvé
        num_cu=matches[0] 
    return num_cu      

def check_address_with_city(text:str,nlp)->tuple[bool, str,str] :
    """
    Vérifie si le format du texte est de la forme: <adresse> à <ville>
    """
    regex_adresse_avec_ville=r"(Demeur.*à)?(?P<adresse>.*)à(?P<ville>.*)\n?"
    match = re.search(regex_adresse_avec_ville, text, re.IGNORECASE)
    if match!=None :
        _rue = match.group("adresse")
        _ville = match.group("ville")
        ville=""
        rue=""
        # Verifier qu'on a bien à faire à une adresse et /ou un ville 
        txt = f"{_rue}\n{_ville}"
        doc = nlp(txt)
        for ent in doc.ents:
            if ent.label_=="ADRESSE" :
                rue = get_rue(ent.text, nlp)
            elif ent.label_=="VILLE" :
                ville = get_ville(ent.text,nlp)
        if rue!=""  or ville!="": 
            return True,rue,ville
    return False, "",""

def get_rue(text:str, nlp) -> str :
    """
    Retourne la rue issue du texte en fonction du comparateur fourni
    """
    _text=text.lower()
    rue=""
    wellknwon_street ='rue du carrouge'
    wellknwon_street2 ="rue de lattre de tassigny"
    wellknwon_street3 ="rue maréchal de lattre de tassigny"
    wellknwon_street4 ='12 rue du carrouge'
    wellknwon_street5 ='12 rue du carouge'
    if wellknwon_street in _text or wellknwon_street2 in _text or wellknwon_street3 in _text or _text in wellknwon_street4 or _text in wellknwon_street5:
        return ""
    rue_comparator:TextComparator=TextComparator(wellknwon_street,nlp)
    rue_comparator2:TextComparator=TextComparator(wellknwon_street2,nlp)
    rue_comparator3:TextComparator=TextComparator(wellknwon_street3,nlp)
    rue_comparator4:TextComparator=TextComparator(wellknwon_street4,nlp)
    rue_comparator5:TextComparator=TextComparator(wellknwon_street4,nlp)
    limit:float=0.85
    if rue_comparator.compare_to(_text)<limit and rue_comparator2.compare_to(_text)<limit and rue_comparator3.compare_to(_text)<limit and rue_comparator4.compare_to(_text)<limit and rue_comparator5.compare_to(_text)<limit:
        rue=text
        logger.debug(f"rue= {rue}" )
    return rue
        
def get_ville(text:str,nlp) ->str:
    """
    """
    ville=""           
    if len(text)<3 : return ""
    _text= text.lower()
    wellknown_city="autun"
    wellknown_city2="plan"
    if wellknown_city in _text or wellknown_city2 in _text:
        return ""
    ville_comparator:TextComparator=TextComparator(wellknown_city)            
    if ville_comparator.compare_to(_text)<0.85 :
        ville = text                                    
        logger.debug(f"ville= {ville}")    
    return ville
def get_code_postal(text:str,nlp)->str :
    """
    """    
    cp_comparator:TextComparator=TextComparator('71400',nlp)
    cp=""
    if cp_comparator.compare_to(text)<0.9 :
        cp=text
        logger.debug(f"cp= {cp}")    
    return cp
    
@measure_time_async
async def extract_cu_basic_data(file_path) ->tuple[int,str,str,str,str]:
    """
    retourne code, erreur_message, num_cu,adresse, cadastre
    """
    text:str
    tables:list[lxfTable] 
    num_cu:str=""
    num_cu_found:bool=False
    adresse:str=""
    adresse_found=False
    cadastre:str=""
    cadastre_found:bool=False
    nlp = load_model()

    # Rechercher d'abord dans les tableaux s'il y en a 
    _,tables = await extract_text_and_table_from_file(file_name=file_path,layout=True,extract_tables=True, extract_text=False)
    if tables!=None :     
        # gestion des tableaux
        for table in tables: 
            if num_cu_found and adresse_found and cadastre_found : break
            
            for row in table.rows :
                if num_cu_found and adresse_found and cadastre_found : break
                for cell in row.cells :                     
                    done:bool=False
                    if num_cu_found and adresse_found and cadastre_found : break
                    valeur = cell.value 
                    if num_cu=="" and num_cu_found==False:
                        num_cu= get_numero_cu(valeur)
                        num_cu_found = num_cu!=""                        
                        if num_cu_found : done=True     
                    if done==False :
                        doc =nlp(valeur)
                        if adresse_found==False or cadastre_found==False :
                            # L'adresse et la ville et le CP doit être dans la même cellule
                            rue:str=""
                            cp:str=""
                            ville:str=""   
                            for ent in doc.ents : 
                                if adresse_found == False :
                                    if ent.label_ =="ADRESSE" and rue=="" :                                 
                                        # il faut gérer les adresses qui contiennent la ville :
                                        # 147 rue des Lilas à Aix-en-Provence
                                        is_city_included, _rue,_ville = check_address_with_city(ent.text, nlp)                              
                                        if is_city_included : 
                                            if _rue!="" : rue =_rue
                                            if _ville!="" : ville = _ville
                                        else :
                                            rue=get_rue(ent.text,nlp)
                                    elif ent.label_=="CODE_POSTAL" and cp=="" :                                 
                                        cp=get_code_postal(ent.text,nlp)
                                    elif ent.label_=='VILLE' and ville =="":
                                        ville = get_ville(ent.text, nlp)                            
                                if ent.label_ == "CADASTRE" and cadastre_found==False:
                                        cadastre=ent.text
                                        cadastre_found=True
                            # L'adresse et la ville et le CP doit être dans la même cellule
                            if adresse_found == False and rue!="" or ville!="" or cp!="":
                                # qu'a-t-on trouvé ? 
                                adresse = f'{rue} {cp} {ville}'.strip()
                                if adresse!="" :
                                    logger.debug(f"Adresse= {adresse}") 
                                    adresse_found=True                   
                            if cadastre_found : 
                                logger.debug(f"Cadastre= {cadastre}")
    # Effectuer une reconnaissance par traitement image 
    if num_cu_found==False or adresse_found == False  or cadastre_found==False :
        pages = await do_OcrImage_from_pdf(file_path,min_high=20,threshold_limit=120,kernel_blur_size=(15,5), kernel_dilated_size=(25,5))
        if pages!=None and len(pages)>0 :
            rue:str=""
            cp:str=""
            ville:str=""   
            for rois in pages :
                for text in rois:              
                    text = sanitize_text(text)
                    done:bool=False
                    if num_cu=="" and num_cu_found==False:
                        num_cu= get_numero_cu(text)
                        num_cu_found = num_cu!=""  
                        if num_cu_found : 
                            done=True    
                    if done==False :
                        doc =nlp(text)  
                        if adresse_found==False or cadastre_found==False :
                                    
                            for ent in doc.ents :                             
                                if adresse_found == False :
                                    if ent.label_ =="ADRESSE" and rue=="" :   
                                        # il faut gérer les adresses qui contiennent la ville :
                                        # 147 rue des Lilas à Aix-en-Provence
                                        is_city_included, _rue,_ville = check_address_with_city(ent.text, nlp)                              
                                        if is_city_included : 
                                            if _rue!="" : rue =_rue
                                            if _ville!="" : ville = _ville
                                        else :
                                            rue=get_rue(ent.text,nlp)
                                    elif ent.label_=="CODE_POSTAL" and cp=="" :                                 
                                        cp=get_code_postal(ent.text,nlp)
                                    elif ent.label_=='VILLE' and ville =="":
                                        ville = get_ville(ent.text, nlp)                              
                                if ent.label_ == "CADASTRE" and cadastre_found==False:
                                        cadastre=ent.text
                                        cadastre_found=True
                            if adresse_found == False  and rue!="" and ville!="":
                                # qu'a-t-on trouvé ? 
                                adresse = f'{rue} {cp} {ville}'.strip()
                                if adresse!="" :
                                    logger.debug(f"Adresse= {adresse}") 
                                    adresse_found=True                   
                            if cadastre_found : 
                                logger.debug(f"Cadastre= {cadastre}")                    
            
        else :
            # Rechercher dans le texte s'il reste encore des données à récupérer    
            text,_ = await extract_text_and_table_from_file(file_name=file_path,layout=True,extract_tables=False, extract_text=True)                                      
            if text!=None and text!="" and (num_cu_found==False or adresse_found==False or cadastre_found==False):
                # gestion du text
                results:list[dict[str, str]] =decouper_text_par_titres(text)
                if len(results)> 0 :
                    for result in results : 
                        for key in result :
                            done:bool=False
                            text = result[key]
                            if num_cu=="" and num_cu_found==False:
                                num_cu= get_numero_cu(text)
                                num_cu_found = num_cu!=""   
                                if num_cu_found : done=True                                           
                            if done==False :
                                doc =nlp(text)
                                if adresse_found==False or cadastre_found==False :
                                    rue:str=""
                                    cp:str=""
                                    ville:str=""
                                    for ent in doc.ents : 
                                        if adresse_found == False :
                                            if ent.label_ =="ADRESSE" and rue=="" :                                 
                                                # il faut gérer les adresses qui contiennent la ville :
                                                # 147 rue des Lilas à Aix-en-Provence
                                                is_city_included, _rue,_ville = check_address_with_city(ent.text, nlp)                              
                                                if is_city_included : 
                                                    if _rue!="" : rue =_rue
                                                    if _ville!="" : ville = _ville
                                                else :
                                                    rue=get_rue(ent.text,nlp)
                                            elif ent.label_=="CODE_POSTAL" and cp=="" :                                 
                                                cp=get_code_postal(ent.text,nlp)
                                            elif ent.label_=='VILLE' and ville =="":
                                                ville = get_ville(ent.text, nlp)  
                                        
                                        if ent.label_ == "CADASTRE" and cadastre_found==False:
                                                cadastre=ent.text
                                                cadastre_found=True
                                    if adresse_found == False and rue!="" and ville!="":
                                        # qu'a-t-on trouvé ? 
                                        adresse = f'{rue} {cp} {ville}'.strip()
                                        if adresse!="" :
                                            logger.debug(f"Adresse= {adresse}") 
                                            adresse_found=True                   
                                    if cadastre_found : 
                                        logger.debug(f"Cadastre= {cadastre}")                            
                else :
                    # Pas de découpage par titre :( 
                    text = sanitize_text(text)
                    if num_cu=="" and num_cu_found==False:
                        num_cu= get_numero_cu(text)
                        num_cu_found = num_cu!=""
                    if num_cu_found : 
                        # il faut supprimer le n° de CU trouvé afin de ne plus l'analyser par NLP
                        text=text.replace(num_cu," XXXXXXXXXXXXX ")
                    doc =nlp(text)
                    if adresse_found==False or cadastre_found==False :
                        rue:str=""
                        cp:str=""
                        ville:str=""
                        for ent in doc.ents : 
                            if adresse_found == False :
                                if ent.label_ =="ADRESSE" and rue==""  :                                 
                                    # il faut gérer les adresses qui contiennent la ville :
                                    # 147 rue des Lilas à Aix-en-Provence
                                    is_city_included, _rue,_ville = check_address_with_city(ent.text, nlp)                              
                                    if is_city_included : 
                                        if _rue!="" : rue =_rue
                                        if _ville!="" : ville = _ville
                                    else :
                                        rue=get_rue(ent.text,nlp)
                                elif ent.label_=="CODE_POSTAL" and cp=="":                                 
                                    cp=get_code_postal(ent.text,nlp)
                                elif ent.label_=='VILLE' and ville=="":                            
                                    ville = get_ville(ent.text, nlp)                            
                            if ent.label_ == "CADASTRE" and cadastre_found==False:
                                    cadastre=ent.text
                                    cadastre_found=True
                        if adresse_found == False and rue!="" and ville!="":
                            # qu'a-t-on trouvé ? 
                            adresse = f'{rue} {cp} {ville}'.strip()
                            if adresse!="" :
                                logger.debug(f"Adresse= {adresse}") 
                                adresse_found=True                   
                        if cadastre_found : 
                            logger.debug(f"Cadastre= {cadastre}")                        
            
    return 0,"Ok",num_cu,adresse, cadastre