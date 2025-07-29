import logging
from lxf.settings import get_logging_level, load_model
#logger
logger = logging.getLogger('Keys words and phrases')
fh = logging.FileHandler('./logs/keysword_and_phrases.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)

# Loading NLP
nlp_ts =load_model()

import math
import random
import time
import re
from typing import List
from pydantic import BaseModel,Field

from lxf.domain.keyWord import KeyWord 
from lxf.domain.keyphrase import KeyPhrase
from lxf.services.measure_time import measure_time






from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 4096,
    chunk_overlap=256,
    length_function = len,
    is_separator_regex = False,
)

from string import punctuation
from spacy.lang.fr.stop_words import STOP_WORDS
chiffres ={"0","1","2","3","4","5","6","7","8","9"}
STOP_WORDS.update(chiffres)
symbols={"€","£","|","§","*"}
STOP_WORDS.update(symbols)
punctuations ={punct for punct in punctuation}
STOP_WORDS.update(punctuations)
miscellanous ={"mr","m.","mme","mlle","me","dr","aucun"}
STOP_WORDS.update(miscellanous)

@measure_time
def sanitize_text(text:str)->str :

    text=text.replace('(',' ( ').replace(')',' ) ').replace('–','-').replace('’','\'').replace("\n"," ").strip()
    # for stop in STOP_WORDS :
    #     text=text.replace(stop,"")
    # remove extra space
    regex = r" {2,}"
    subst = " "
    # You can manually specify the number of replacements by changing the 4th argument
    return re.sub(regex, subst, text, 0, re.MULTILINE | re.DOTALL)

@measure_time
def sub_divide(document,sep:str):
    result=[]
    for phrase in document:
        sub_phrases = phrase.split(sep)
        for sub in sub_phrases:
            result.append(sanitize_text(sub))
    return result

chunks_limit:int=30
class KeysWordsPhrases(BaseModel):
	keysWords:List[KeyWord]=Field(default=[])
	keysPhrases:List[KeyPhrase]=Field(default=[])
	class Config:       
		arbitrary_types_allowed = True 
		json_schema_extra = {
			"example": {
				"keysWords": [
					{
						"word": "montant",
						"freq": 1
					}
				],
				"keysPhrases": []
			}		
		}


class KeysWordsAndPhrases:
    """
    Keys words and keys phrases from Text
    """
    def __init__(self,text:str) :
        self.internalText=text[:nlp_ts.max_length-1024]
    
    @measure_time 
    def get_key_words(self,
        importantes_entites=["ORG_PUBLIC","PERSONNE","GARANTIE_FINANCIERE","QUALITE","ARTICLE_LOI","CODE_JURIDIQUE","TAUX_BANCAIRE","DELEGATION_BANQUE_ASSURANCE","METIER","VILLE","ORG"],
        importants_lemma=["testament","cadastre","signature","procuration","maritale","métier","partage","iban","vente","répertoire","banque","syndic","convention","bail","confidentialité","imposition",
                            "mairie","état-civil","officiel","authentique","copie","exécutoire","mariage","naissance","décés","emprunteur","assurance","hypothèque","caution","devis",
                            "prêteur","diagnostic","certificat","urbanisme","prêt","représenter","facture","honoraire","signer","délèguer","authentique","crédit","emprunt","relance","devoir",
                            "taux","acte","prêteur","emprunteur","héritier","honoraire","notaire","clerc","avocat","huissier","juge","relance","réquisition","certificat","minute","brevet",
                            "donataire","donateur","donation","statut","kbis","contrat","kbis","greffe","tribunal","commerce","trésor","impôt","ursaff","juridique","mandat"],
        threshold:float=0.15,
        isSorted:bool=True,
        entity_booster_inc:float=4,
        lemma_booster_inc:float=4):
        """
        """
        try:   
            t= time.time()                     
            logger.debug("Start measuring get_keys_words")
            text = self.internalText
            if text ==None or text == "":                
                return None
            text = sanitize_text(text)
            #logger.debug(f"Text récupéré: \n{text}")
            splitted_text=text_splitter.split_text(text)
            logger.debug(f"Splitted (Len={len(splitted_text)}) text completed at {(time.time()-t):.4f}")    

            freq_mots={}
            limit:int=len(splitted_text)
            if limit>chunks_limit:
                limit=chunks_limit                
            for chunk in splitted_text[:limit] :
                t_chunk=time.time()
                document = nlp_ts(chunk)
                logger.debug(f"NLP chunk document loaded in {(time.time()-t_chunk):.4f} secondes")
                for mot in document:   
                    # ne pas prendre pas les mots de taille inférieur ou égale 2 caractères
                    if len(mot) >2 :             
                        mot_lower= mot.lemma_.lower().replace('(','').replace(')','')
                        if not (mot.is_digit or mot.is_space or mot.is_bracket or mot.is_punct or mot.is_quote or mot.like_num) and len(mot_lower)>1 :
                            if mot_lower not in STOP_WORDS :
                                if mot_lower not in freq_mots.keys():
                                    freq_mots[mot_lower]=1
                                else :
                                    freq_mots[mot_lower]+=1
                                # boost mot 
                                if mot_lower in importants_lemma:
                                    freq_mots[mot_lower]+= lemma_booster_inc                                
            logger.debug(f"Freq_mots step 1 completed at {(time.time()-t):.4f}")
            if freq_mots !={}  :
                plus_grande_freq=max(freq_mots.values())
                for mot in freq_mots:
                    freq_mots[mot]/=plus_grande_freq
            else: 
                logger.warning("Freq_mots est null")
                # renvoyer dictionnaire vide
                return {}

            logger.debug(f"Freq_mots completed at {(time.time()-t):.4f}")
                            
            # applied threshold on keywords
            # remove all items under threshold value 
            keysWords={}
            logger.debug(f"Threshold : {threshold}")
            if freq_mots!=None :
                for mot,freq in freq_mots.items():
                    if freq >= threshold : 
                        keysWords[mot]=freq  

            logger.debug(f"freq_mot threshold completed at {(time.time()-t):.4f}") 
            # Cleanup 
            if freq_mots!=None :
                freq_mots.clear()   
            if isSorted and keysWords.items!=None:
                freq_mot_sorted= dict(sorted(keysWords.items(),key=lambda x:x[1],reverse=True))
                logger.debug(f"freq_mot sorted at {(time.time()-t):.4f}")
                return freq_mot_sorted
            return keysWords
        except Exception as ex :
            logger.critical(f"Exception KeysWordsAndPhrases.get_keys_words:  {ex}")
            return {}

    @measure_time
    def get_key_words_phrases(self,
                        importantes_entites=["ORG_PUBLIC","PERSONNE","GARANTIE_FINANCIERE","QUALITE","ARTICLE_LOI","CODE_JURIDIQUE","TAUX_BANCAIRE","DELEGATION_BANQUE_ASSURANCE","METIER","VILLE","ORG"],
                        importants_lemma=["vente","prêt","représenter","facture","honoraire","signer","délèguer","procuration","authentique","crédit","emprunt","solde","montant","relance","devoir","taux","acte","avoir","prêteur","emprunteur","héritier","honoraire","notaire","avocat","huissier","juge","relance","donataire","donateur","donation","achat"],
                        threshold:float=0.1,
                        isSorted:bool=True,
                        entity_booster_inc:float=4.5,
                        lemma_booster_inc:float=2.5):
        try:                        
            text = self.internalText
            if text ==None or text == "":                
                raise ValueError("aucun texte extrait")
            #logger.debug(f"Text récupéré: \n{text}")
            t = time.time()
            splitted_text=text_splitter.split_text(text)
            logger.debug(f"Splitted (Len={len(splitted_text)}) text completed at {(time.time()-t):.4f}") 
            
            freq_mots={}
            limit:int=len(splitted_text)
            if limit>30:
                limit=30
            for chunk in splitted_text[:limit] :
                t_chunk=time.time()
                document = nlp_ts(chunk)
                logger.debug(f"NLP chunk document loaded in {(time.time()-t_chunk):.4f} secondes")            
                for mot in document:                
                    mot_lower= mot.lemma_.lower()
                    if not (mot.is_digit or mot.is_space or mot.is_bracket or mot.is_punct or mot.is_quote or mot.like_num) and len(mot_lower)>1 :

                        if mot_lower not in STOP_WORDS :
                            if mot_lower not in freq_mots.keys():
                                freq_mots[mot_lower]=1
                            else :
                                freq_mots[mot_lower]+=1
                            # boost mot 
                            if mot_lower in importants_lemma:
                                freq_mots[mot_lower]+= lemma_booster_inc
                                logger.debug(f"Boost mot by LEMMA: {mot_lower} freq : {freq_mots[mot_lower]}")

            plus_grande_freq=max(freq_mots.values())

            for mot in freq_mots:
                freq_mots[mot]/=plus_grande_freq
           
            # Phrases scoring 
            phrases=sub_divide([text],sep=".")
            phrases=sub_divide(phrases,sep=";") 

            phrases=sub_divide(phrases,sep="- ")             
            scores_phrases={}
            for phrase in phrases:
                ph=nlp_ts(phrase)
                nb_mots_comptes=0
                for mot in ph:              
                    if not (mot.is_digit or mot.is_space or mot.is_bracket or mot.is_punct or mot.is_quote or mot.like_num) and len(mot)>1: 
                        lower_mot=mot.lemma_.lower()  
                        if not lower_mot in STOP_WORDS :
                            if lower_mot in freq_mots.keys() :
                                nb_mots_comptes+=1
                                if ph in scores_phrases.keys():
                                    scores_phrases[ph]+=freq_mots[lower_mot]
                                else :
                                    scores_phrases[ph]=freq_mots[lower_mot]
                #normalized by the number of words taken by the phrase score computation
                if nb_mots_comptes > 0 :
                    scores_phrases[ph]= float(scores_phrases[ph])/nb_mots_comptes
            # boosting the phrases scoring based on entity type or lemma
            maxScore:float=0.0
            for phrase, score in scores_phrases.items():
                entity_booster=0
                lemma_booster=0
                for ent in phrase.ents :
                    logger.debug(f"Entité {ent.label_} => {ent.text}")
                    if ent.label_ in importantes_entites:
                        entity_booster += entity_booster_inc
                for token in phrase:
                    if token.lemma_.lower() in importants_lemma:
                        lemma_booster += lemma_booster_inc
                bias = random.random()
                booster = math.log(entity_booster+lemma_booster+bias)
                if booster > 0 : 
                    # if no entity found or lemma , because log(x)<0 when x <1  where x=entity_booster+lemma_booster+bias 
                    scores_phrases[phrase]=float(score)+booster   
                if scores_phrases[phrase]> maxScore :
                    maxScore = scores_phrases[phrase]
            if maxScore>0 :
                # normalized
                for phrase, score in scores_phrases.items():
                    scores_phrases[phrase]=float(score)/maxScore                     
            # applied threshold on keywords
            # remove all items under threshold value 
            keysWords={}
            logger.debug(f"Threshold : {threshold}")
            for mot,freq in freq_mots.items():
                if freq >= threshold : 
                    keysWords[mot]=freq  
   
            # Cleanup 
            freq_mots.clear()   
            if isSorted :
                return dict(sorted(keysWords.items(),key=lambda x:x[1],reverse=True)), scores_phrases # don't sort the phrase cause meaning will be losted
            return keysWords, scores_phrases
        except Exception as ex :
            raise Exception(f"Exception KeysWordsAndPhrases.get_keys_words:  {ex}")
