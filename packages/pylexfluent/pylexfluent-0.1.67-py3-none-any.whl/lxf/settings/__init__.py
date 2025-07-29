import logging
import os
from sentence_transformers import SentenceTransformer, util
import spacy
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from torch import cuda

if spacy.prefer_gpu() :
    print("Spacy will use GPU")
else :
    print("Spacy will use CPU")

global nlp_with_vectors
try:
    print("Chargement du modèle SPACY : fr_core_news_lg ")
    nlp_with_vectors = spacy.load("fr_core_news_lg")
except Exception as ex:
    nlp_with_vectors=None
    print("le model SPACY : fr_core_news_lg est obligatoire. Exécuter la ligne de commande suivante: python -m spacy download fr_core_news_lg ")

global nlp
nlp=None
global model_path
model_path='models/nlp/lex-fr.nlp'

global enable_tqdm
enable_tqdm:bool=False

global SET_LOGGING_LEVEL
SET_LOGGING_LEVEL = logging.ERROR

# Chargement du modèle d'embedding SentenceTransformer
global sentence_embedding_model
sentence_embedding_model = SentenceTransformer('all-MiniLM-L6-v2', tokenizer_kwargs={"clean_up_tokenization_spaces": True})

# Chargement du modèle de summarization
device = "cuda" if cuda.is_available() else "cpu"
model_name = "facebook/mbart-large-50"
global text_tokenizer
text_tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
text_tokenizer.src_lang = "fr_XX"
global text_summarization_model
text_summarization_model = MBartForConditionalGeneration.from_pretrained(model_name).to(device)



def get_logging_level():
    """
    Return the current LOGGING LEVEL : DEBUG=10, ERROR=40 
    """
    return SET_LOGGING_LEVEL

def set_logging_level(logging_level)->None:
    """
    Change the current Logging 
    """
    global SET_LOGGING_LEVEL
    SET_LOGGING_LEVEL=logging_level

if os.path.exists("./logs") ==False:
    print("Création du dossier logs")
    os.mkdir("./logs")

def load_model(path:str=None):
    """
    """
    global model_path
    global nlp
    if path!=None and path!=model_path:
        model_path=path        
        if os.path.exists(model_path) :
            print(f"Chargement du modèle depuis: {model_path}")
            nlp=spacy.load(model_path)
        else :
            print(f"Erreur: le modèle est introuvable: {model_path}")
            return None            
    if nlp==None:
        nlp=spacy.load(model_path)
    return nlp


global nlp_title
nlp_title=None
global model_title_path
model_title_path="models/nlp/lex-title-model-trained-V2/model-best"

def load_model_title(path:str=None):
    """
    """
    global model_title_path
    global nlp_title
    if path!=None and path!=model_title_path:
        model_title_path=path        
        if os.path.exists(model_title_path) :
            print(f"Chargement du modèle depuis: {model_title_path}")
            nlp_title=spacy.load(model_title_path)
        else :
            print(f"Erreur: le modèle est introuvable: {model_title_path}")
            return None            
    if nlp_title==None:
        nlp_title=spacy.load(model_title_path)
    return nlp_title