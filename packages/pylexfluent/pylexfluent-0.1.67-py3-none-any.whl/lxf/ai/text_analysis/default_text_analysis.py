
import logging
from typing import Dict, List, Tuple
from lxf import settings

from lxf.services.measure_time import measure_time
#logger
logger = logging.getLogger('Text Analysis')
fh = logging.FileHandler('./logs/default_text_analysis.log')
fh.setLevel(settings.get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(settings.get_logging_level())
logger.addHandler(fh)
import regex
import re
from sentence_transformers import util

import numpy as np


from torch import cuda
from lxf.settings import load_model_title, nlp_with_vectors , text_summarization_model , sentence_embedding_model , text_tokenizer


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
    # Supprimer les espaces entre les lettres d'un mot
    text = re.sub(r"([A-Za-z]) ([A-Za-z]) ", r"\g<1>\g<2>", text)
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
    # text = re.sub(regex, "", text)
    # Les caractères blancs consécutifs
    regex = r" {2,}"
    subst=" "
    text = re.sub(regex, subst, text, 0, re.MULTILINE)
    # text=re.sub(r'^[ \t]+|[ \t]+$',' ',text)
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
    # regex = r"\n *?(?P<minuscule>[a-z0-9àéèêïöôë])"
    # subst = r" \g<minuscule>" 
    # text = re.sub(regex, subst, text, 0, re.MULTILINE)
        #listes a puces
    # regex=r'\n-'
    # subst='\n•'
    # text=re.sub(regex,subst,text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def is_validate_title(text: str, context: str = "") -> tuple[bool, str]:
    """
    Verifie qu'il s'agit bien d'un titre
    """
    #Verifier qu'il y a au moins une majuscule
    rule_has_one_capital_at_least=r"[A-Z]" 
    matches = re.search(rule_has_one_capital_at_least,text)
    if matches==None :
        return False, None
    
    # Vérification de la longueur du contexte
    rule0=r"\n*.{1,60}\n"
    # Vérifier si le titre commence par une suite de chiffres
    rule1 = r"[0-9]{4,}[,.\s]?[A-Za-z]*"
    # Détecter une suite de caractères spéciaux
    rule2 = r"^[\.\-\%\&\+\±\/]{2,}" # \(\)  on enlève ce cas car on a des titres par exemple : ASSURANCE(S) 
    # Détecter un titre commençant par exactement deux lettres sauf exceptions
    rule3 = r"^\b([a-zA-Z]{2})\b"
    # Détecter si un titre commence par une ponctuation
    rule_punctuation = r"^[^\w\d]"
    # Vérifier si un mot contient trop de consonnes
    rule_consonnes = r"[BCDFGHJKLMNPQRSTVWXZbcdfghjklmnpqrstvwxz$\[\)\(\!\?\+\&\%\#\;\:\@\,\'\"\\x]{4,}"

    exceptions = {"le", "la", "un", "une", "du", "de", "au", "en"}
    
    if len(text.strip()) < 3:
        return False, None
    # Vérification du contexte
    if re.match(rule0, context) is None:
        return False, None

    mots = text.split()
    if not mots:  
        return False, None

    premier_mot = mots[0] 

    # Rejeter le titre si le premier mot est invalide
    if re.search(rule1, premier_mot):  
        return False, None
    if re.search(rule2, premier_mot): 
        return False, None
    if (re.search(rule_consonnes,mots[0]) != None):
        return False ,None
    if re.match(rule_punctuation, premier_mot):  
        return False, None

    match_rule3 = re.match(rule3, premier_mot, re.IGNORECASE | re.MULTILINE)
    if match_rule3:
        first_word = match_rule3.group(1).lower()
        if first_word not in exceptions:
            return False, None

    # Si le premier mot est valide, on garde tout le titre
    return True, text

@measure_time
def extract_titles(text: str) -> List[str]:
    """
    """
    text=sanitize_document(text)
    nlp_title = load_model_title()
    titles = []
    if nlp_title !=None :
        doc=nlp_title(text)
        for ent in doc.ents :
            if ent.label_=="TITRE" :
                context:str=text[ent.start_char:ent.start_char+80]
                valide , valide_tile = is_validate_title(ent.text,context)
                if valide :
                    titles.append({ 
                        "titre":valide_tile,
                        "debut":ent.start_char,
                        "fin":ent.end_char
                    })
    else :
        title_regex = r"^(?!\s*(P\s*[Aa]\s*[Gg]\s*[Ee])\b)(?![A-Z0-9./\- ]{2,10}$)[0-9.]{0,}(I|II|III|IV|V|VI)*[)\.\- ]{0,} *[A-Z][A-Z’']*[a-z’']*[^!?,:;.]{1,60}$"
        for match in re.finditer(title_regex, text, re.MULTILINE):
            titles.append({
                "titre": match.group(0).strip(),
                "debut": match.start(),
                "fin": match.end()
            })
    nlp_title=None
    return titles


def decouper_text_par_titres(text: str) -> List[Dict[str, str]]:
    titres_positions = extract_titles(text)
    text = sanitize_document(text)
    sections = []
    if titres_positions and titres_positions[0]["debut"] > 0:
        sections.append({
            "titre": "Introduction (avant le premier titre)",
            "contenu": text[:titres_positions[0]["debut"]].strip()
        })
    titres_fusionnes = titres_positions[:]
    for i, titre_position in enumerate(titres_fusionnes):
        debut_contenu = titre_position["fin"]
        if i < len(titres_fusionnes) - 1:
            fin_contenu = titres_fusionnes[i + 1]["debut"]
        else:
            fin_contenu = len(text)
        contenu = text[debut_contenu:fin_contenu].strip()
        if not contenu:
            if i < len(titres_fusionnes) - 1:
                titres_fusionnes[i + 1]["titre"] = titre_position["titre"] + "\n" + titres_fusionnes[i + 1]["titre"]
            continue  
        sections.append({
            "titre": titre_position["titre"],
            "contenu": contenu
        })
    return sections


@measure_time
def segment_text_into_chunks(text, buffer_size=32, breakpoint_percentile_threshold=90)->List[str]:
    #model = sentence_embedding_model
    text = sanitize_document(text)   
    paragraphs = regex.split(r'\n{2,}', text)

    all_chunks = []

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        single_sentences_list = regex.split(
            r'(?<!\b(?:M\.|Dr\.|Art\.|Prof\.|Mme\.|St\.|Ex\.|etc\.))(?<!\d\.)(?<=[.?!])\s+', 
            paragraph
        )
        sentences = [{'sentence': x, 'index': i} for i, x in enumerate(single_sentences_list)]
        sentences = combine_sentences(sentences, buffer_size=buffer_size)
        embeddings = sentence_embedding_model.encode([sentence['combined_sentence'] for sentence in sentences])
        if len(embeddings) > 1:
            distances = [1 - util.cos_sim(embeddings[i], embeddings[i + 1])[0].item() for i in range(len(embeddings) - 1)]
        else:
            all_chunks.append(paragraph)
            continue
        breakpoint_distance_threshold = np.percentile(distances, breakpoint_percentile_threshold)
        indices_above_thresh = [i for i, distance in enumerate(distances) if distance > breakpoint_distance_threshold]
        start_index = 0
        for index in indices_above_thresh:
            end_index = index + 1
            chunk = ' '.join([sentences[i]['sentence'] for i in range(start_index, end_index + 1)])
            all_chunks.append(chunk)
            start_index = end_index + 1
        if start_index < len(sentences):
            chunk = ' '.join([sentences[i]['sentence'] for i in range(start_index, len(sentences))])
            all_chunks.append(chunk)

    return all_chunks

def lemmatize_and_extract_entities(text)->Tuple[str, List[Dict[str, str]]]:
    """
    Effectue la lemmatisation tout en détectant les entités nommées.
    """
    nlp = nlp_with_vectors
    doc = nlp(text)
    
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    words_to_preserve={"madame","monsieur","mademoiselle","Madame","Monsieur","Mademoiselle","Mesdames", "Messieurs","Docteur", "Professeur","RIB", "IBAN","km", "kg", "€", "$"}

    lemmatized_text = " ".join([
        token.text if token.text in words_to_preserve or token.ent_type_ else token.lemma_
        for token in doc
    ])    
    nlp=None
    return lemmatized_text, entities


def split_large_chunk(chunk: str, max_length: int, tokenizer) -> List[str]:
    """
    """
    if not chunk.strip():
        return []
    tokens = tokenizer.encode(chunk, truncation=False, add_special_tokens=False)
    if not tokens:
        return []
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_length, len(tokens))

        if end < len(tokens):
            for i in range(end - 1, start - 1, -1):  
                if tokenizer.decode([tokens[i]]) in {".", "!", "?"}:
                    end = i + 1  
                    break

        subchunk_tokens = tokens[start:end]
        subchunk = tokenizer.decode(subchunk_tokens, skip_special_tokens=True)
        chunks.append(subchunk.strip())
        start = end
    return chunks

def generate_summary(text: str, max_length=300, min_length=150, num_beams=4) -> str:
    """
    """
    if len(text.split()) < 30:  
        return text 
    device = "cuda" if cuda.is_available() else "cpu"
    inputs = text_tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length).to(device)

    summary_ids = text_summarization_model.generate(
        inputs["input_ids"],
        
        num_beams=num_beams,
        max_length=max_length,
        min_length=min_length,
        early_stopping=True,
        no_repeat_ngram_size=2,
        forced_bos_token_id=text_tokenizer.lang_code_to_id["fr_XX"] 
    )
    return text_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def summarize_chunks(text: str, summary_max_length: int = 1024) -> List[str]:
    """
    """
    logger.debug("Segmentation du texte en chunks...")
    chunks = segment_text_into_chunks(text)

    logger.debug("Division des chunks trop grands...")
    all_subchunks = []
    for chunk in chunks:
        subchunks = split_large_chunk(chunk, max_length=summary_max_length, tokenizer=text_tokenizer)
        all_subchunks.extend(subchunks)

    logger.debug("Generation des resumes intermediaires...")
    chunk_summaries = []
    for i, subchunk in enumerate(all_subchunks):
        try:
            summary = generate_summary(subchunk)
            chunk_summaries.append(f"- {summary}")  
            logger.debug(f"Resume intermediaire {i + 1}/{len(all_subchunks)} genere.")
        except Exception as e:
            logger.error(f"Erreur lors du resume intermediaire pour le chunk {i + 1}: {e}")
            # chunk_summaries.append(f"Erreur lors du résumé.")
    return chunk_summaries