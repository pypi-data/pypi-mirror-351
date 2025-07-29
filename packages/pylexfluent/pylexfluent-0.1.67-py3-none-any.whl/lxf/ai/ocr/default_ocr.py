import logging
from typing import Dict, List, Tuple
from lxf import settings
from lxf.domain.tables import lxfTable
from lxf.services.measure_time import measure_time
#logger
logger = logging.getLogger('OCR')
fh = logging.FileHandler('./logs/default_ocr.log')
fh.setLevel(settings.get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(settings.get_logging_level())
logger.addHandler(fh)
import regex
import re
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from lxf.ai.ocr.text_extractor import extract_text_from_image
from pdf2image import convert_from_path
import cv2
import spacy

# model = SentenceTransformer('all-MiniLM-L6-v2')

# with open('/home/lexia/lexia-services/RevolutionAI/Assistants/Conversationnel/chunking_test') as file:
#     essay = file.read()

# single_sentences_list = re.split(r'(?<=[.?!])\s+', essay)
# print(f"{len(single_sentences_list)} sentences were found")
# sentences = [{'sentence': x, 'index': i} for i, x in enumerate(single_sentences_list)]
# print(sentences[:5])

nlp = spacy.load("fr_core_news_lg")

def combine_sentences(sentences, buffer_size=1):
    # Go through each sentence dict
    for i in range(len(sentences)):

        # Create a string that will hold the sentences which are joined
        combined_sentence = ''

        # Add sentences before the current one, based on the buffer size.
        for j in range(i - buffer_size, i):
            # Check if the index j is not negative (to avoid index out of range like on the first one)
            if j >= 0:
                # Add the sentence at index j to the combined_sentence string
                combined_sentence += sentences[j]['sentence'] + ' '

        # Add the current sentence
        combined_sentence += sentences[i]['sentence']

        # Add sentences after the current one, based on the buffer size
        for j in range(i + 1, i + 1 + buffer_size):
            # Check if the index j is within the range of the sentences list
            if j < len(sentences):
                # Add the sentence at index j to the combined_sentence string
                combined_sentence += ' ' + sentences[j]['sentence']

        # Then add the whole thing to your dict
        # Store the combined sentence in the current sentence dict
        sentences[i]['combined_sentence'] = combined_sentence

    return sentences

def sanitize_document(text:str)->str :
    """
    Nettoyage d'un text en lignes , paragraphes..
    """
    # Encadrer les adresses e-mail de guillemets
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\s*\.[A-Z|a-z]{2,}\b'
    text = re.sub(regex, lambda match: '"' + match.group(0).replace(' ', '') + '"', text)
    # Encadrer les URL de guillements
    regex=r'\b(?:http|https|www):?[^\s]+[A-Za-z0-9.-]'
    text =re.sub(regex,lambda match:f'"{match.group(0)}"',text)

    #supprime espaces avant ponctuations
    regex=r'\s+([.,!?;:])'
    text = re.sub(regex, r'\1', text)
    # Ajouter un point aux fins de paragraphes
    # regex = r"(?<!\.)\n"
    # text = re.sub(regex, ".\n", text)
    
    #supprime espace apres ponctuations
    regex = r'(?<=[?!])'
    text = re.sub(regex, '\\g<0> ', text, 0, re.MULTILINE)

    # Supprimer les en-têtes/pieds de page
    regex = r"(Page \d+\/\d+\s*)+"
    text = re.sub(regex, "", text)
    # Les caractères blancs consécutifs
    regex = r" {2,}"
    subst=" "
    text = re.sub(regex, subst, text, 0, re.MULTILINE)
    text=re.sub(r'^[ \t]+|[ \t]+$',' ',text)
    #gestion des guillemets
    regex = r'(?<=[^\s])"(?=[^\s])'
    text = re.sub(regex, ' " ', text)
    # Retours à la ligne suivis d'une majuscule

    # regex = r"\n *?(?P<majuscule>[A-ZÀ])"
    # subst=". \\g<majuscule>"
    # text = re.sub(regex, subst, text, 0, re.MULTILINE)

    # regex=r'(?<![.?!])\n *?(?P<majuscule>[A-ZÀ])'
    # subst=". \\g<majuscule>"
    # text = re.sub(regex, ". \\g<majuscule>", text)

    #Les retours à la ligne restants non suivi d'une majuscule
    regex = r"\n *?(?P<minuscule>[a-z0-9àéèêïöôë])"
    subst = r" \g<minuscule>" 
    text = re.sub(regex, subst, text, 0, re.MULTILINE)
        #listes a puces
    # regex=r'\n-'
    # subst='\n•'
    # text=re.sub(regex,subst,text)
    text =re.sub(r'\n{2,}',' ', text)
    

    return text
@measure_time
def segment_text_into_chunks(text, model_name='all-MiniLM-L6-v2', buffer_size=1, breakpoint_percentile_threshold=95)->List[str]:

    model = SentenceTransformer(model_name, tokenizer_kwargs={"clean_up_tokenization_spaces":True})
    text = sanitize_document(text)   
    single_sentences_list = regex.split(r'(?<!\b(?:M\.|Dr\.|Art\.|Prof\.|Mme\.|St\.|Ex\.|etc\.))(?<!\d[.,])(?<=[.?!])\s+', text)

    sentences = [{'sentence': x, 'index': i} for i, x in enumerate(single_sentences_list)]
    sentences = combine_sentences(sentences, buffer_size=buffer_size)
    
    embeddings = model.encode([sentence['combined_sentence'] for sentence in sentences])
    if len(embeddings) > 1:
        distances = [1 - util.cos_sim(embeddings[i], embeddings[i+1])[0].item() for i in range(len(embeddings)-1)]
    else:
        return [text]
    breakpoint_distance_threshold = np.percentile(distances, breakpoint_percentile_threshold)
    indices_above_thresh = [i for i, distance in enumerate(distances) if distance > breakpoint_distance_threshold]

    chunks = []
    start_index = 0
    for index in indices_above_thresh:
        end_index = index + 1  
        chunk = ' '.join([sentences[i]['sentence'] for i in range(start_index, end_index + 1)])
        chunks.append(chunk)
        start_index = end_index + 1

    if start_index < len(sentences):
        chunk = ' '.join([sentences[i]['sentence'] for i in range(start_index, len(sentences))])
        chunks.append(chunk)

    return chunks



def lemmatize_and_extract_entities(text)->Tuple[str, List[Dict[str, str]]]:
    """
    Effectue la lemmatisation tout en détectant les entités nommées.
    """
    doc = nlp(text)
    
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    lemmatized_text = " ".join([token.lemma_ if not token.ent_type_ else token.text for token in doc])
    
    return lemmatized_text, entities



# async def do_default_ocr(pdf_path: str, use_tesseract=True, use_GPU=True) -> list:
#     """
#     Effectue l'OCR sur chaque page d'un PDF et segmente le texte extrait en chunks.
#     """
#     pages = convert_from_path(pdf_path)
#     all_chunks = []

#     for i, page in enumerate(pages):
#         image_path = f"./data/temp/page_{i+1}.jpeg"
#         page.save(image_path, "JPEG")
#         image = cv2.imread(image_path)
#         if image is None:
#             logger.error(f"Impossible de charger l'image de la page {i+1}.")
#             continue

#         try:
#             extracted_text = extract_text_from_image(image, use_tesseract=use_tesseract, use_GPU=use_GPU)
#             if not extracted_text.strip():
#                 logger.warning(f"Aucun texte détecté sur la page {i+1}, tentative avec Tesseract...")
#                 extracted_text = extract_text_from_image(image, use_tesseract=True, use_GPU=False)
#         except Exception as e:
#             logger.error(f"Erreur OCR sur la page {i+1} : {e}")
#             continue

#         # segmentation du texte extrait en chunks
#         chunks = segment_text_into_chunks(extracted_text)
#         all_chunks.extend(chunks)
#         logger.info(f"{len(chunks)} chunks extraits de la page {i+1}.")

#     return all_chunks







