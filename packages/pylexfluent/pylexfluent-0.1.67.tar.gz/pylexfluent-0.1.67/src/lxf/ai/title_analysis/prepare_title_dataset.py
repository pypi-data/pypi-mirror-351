from lxf.ai.ocr.default_ocr import sanitize_document
from lxf.ai.text_analysis.default_text_analysis import extract_titles, is_validate_title

import logging
from lxf.settings import get_logging_level
logger = logging.getLogger('title analysis')
fh = logging.FileHandler('./logs/prepare_title_dataset.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)


from lxf.ai.classification.classifier import extract_text_from_file
import os
import json
from lxf.settings import load_model_title
import spacy

nlp_title = load_model_title()

async def extract_titles_from_folder(folder_path, output_path):
    """

    """
    examples = []

    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

    if not pdf_files:
        logger.debug(f"Aucun fichier PDF trouvé dans {folder_path}")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        logger.debug(f"Traitement : {pdf_path}...")
        extracted_text = await extract_text_from_file(pdf_path)
        if not extracted_text.strip():
            logger.debug(f"Texte vide pour {pdf_path}")
            continue
        doc = nlp_title(extracted_text)
        for ent in doc.ents:
            if ent.label_ == "TITRE":
                if is_validate_title(ent.text) :

                    examples.append({
                        "text": ent.text.strip(),
                        "meta":{"source":pdf_file},
                    })
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    logger.debug(f"Fichier JSONL créé avec {len(examples)} titres : {output_path}")


async def generer_extraits_pour_prodigy_(dossier_pdfs, chemin_sortie, caracteres_avant=100, caracteres_apres=100):
    extraits = []

    pdf_files = [f for f in os.listdir(dossier_pdfs) if f.endswith(".pdf")]
    if not pdf_files:
        logger.error(f"Aucun fichier PDF trouvé dans {dossier_pdfs}")
        return
    for pdf_file in pdf_files:
        chemin_pdf = os.path.join(dossier_pdfs, pdf_file)
        logger.debug(f"Traitement du fichier : {chemin_pdf}")
        texte_extrait = await extract_text_from_file(chemin_pdf)
        if not texte_extrait.strip():
            logger.debug(f"Texte vide pour {chemin_pdf}")
            continue
        titres_detectes = extract_titles(texte_extrait)
        for titre_info in titres_detectes:
            titre_sans_saut = titre_info["titre"]
            start = titre_info["debut"]
            end = titre_info["fin"]
            if start == -1 or end == -1:
                logger.debug(f"Impossible de retrouver le titre dans {pdf_file}")
                continue
            debut_extrait = max(0, start - caracteres_avant)
            fin_extrait = min(len(texte_extrait), end + caracteres_apres)
            extrait_autour_titre = texte_extrait[debut_extrait:fin_extrait]
            # Ajout des spans
            # titres_extraits = extract_titles(extrait_autour_titre)
            # spans = []
            # for titre_info_extrait in titres_extraits:
            #     titre_extrait =titre_info_extrait["titre"]
            #     start_in_extrait= titre_info_extrait["debut"]
            #     end_in_extrait =titre_info_extrait["fin"]

            #     spans.append({
            #         "text": titre_extrait,
            #         "start": start_in_extrait,
            #         "end": end_in_extrait,
            #         "label": "TITRE"
            #     })

            # if spans:
            #     extraits.append({
            #         "text": extrait_autour_titre,
            #         "spans": spans,
            #         "meta": {"source": pdf_file}
            #     })
            extraits.append({
                "text": extrait_autour_titre,
                "meta": {"source": pdf_file}
            })

    with open(chemin_sortie, 'w', encoding='utf-8') as f:
        for exemple in extraits:
            f.write(json.dumps(exemple, ensure_ascii=False) + '\n')

    logger.debug(f"JSONL pour Prodigy créé : {chemin_sortie} avec {len(extraits)} extraits.")



def align_span_with_tokens(span_start, span_end, doc):
    """
    Ajuste les positions d'un span pour qu'elles correspondent aux limites des tokens de spaCy.
    """
    span_start_aligned = None
    span_end_aligned = None

    for token in doc:
        if span_start_aligned is None and token.idx <= span_start < token.idx + len(token.text):
            span_start_aligned = token.idx

        if token.idx <= span_end <= token.idx + len(token.text):
            span_end_aligned = token.idx + len(token.text)

    if span_start_aligned is None or span_end_aligned is None:
        return None, None

    return span_start_aligned, span_end_aligned

async def generer_extraits_pour_prodigy(dossier_pdfs, chemin_sortie, caracteres_avant=100, caracteres_apres=100):
    extraits = []

    pdf_files = [f for f in os.listdir(dossier_pdfs) if f.endswith(".pdf")]
    if not pdf_files:
        logger.error(f"Aucun fichier PDF trouvé dans {dossier_pdfs}")
        return
    nlp = spacy.load("fr_core_news_lg")
    for pdf_file in pdf_files:
        chemin_pdf = os.path.join(dossier_pdfs, pdf_file)
        logger.debug(f"Traitement du fichier : {chemin_pdf}")
        texte_extrait = await extract_text_from_file(chemin_pdf)
        if not texte_extrait.strip():
            logger.debug(f"Texte vide pour {chemin_pdf}")
            continue

        # Tokenisation du texte avec spaCy

        doc = nlp(texte_extrait)

        titres_detectes = extract_titles(texte_extrait)
        texte_extrait=sanitize_document(texte_extrait)
        for titre_info in titres_detectes:
            titre_sans_saut = titre_info["titre"]
            start = titre_info["debut"]
            end = titre_info["fin"]
            if start == -1 or end == -1:
                logger.debug(f"Impossible de retrouver le titre dans {pdf_file}")
                continue

            # Ajuster les positions du span pour qu'elles correspondent aux tokens
            start_aligned, end_aligned = align_span_with_tokens(start, end, doc)
            if start_aligned is None or end_aligned is None:
                logger.debug(f"Impossible d'aligner le span pour le titre : {titre_sans_saut}")
                continue

            debut_extrait = max(0, start_aligned - caracteres_avant)
            fin_extrait = min(len(texte_extrait), end_aligned + caracteres_apres)
            extrait_autour_titre = texte_extrait[debut_extrait:fin_extrait]

            # Tokenisation de l'extrait
            doc_extrait = nlp(extrait_autour_titre)
            tokens_extrait = [
                {"text": token.text, "start": token.idx, "end": token.idx + len(token.text), "id": i}
                for i, token in enumerate(doc_extrait)
            ]

            titres_extraits = extract_titles(extrait_autour_titre)
            spans = []
            for titre_info_extrait in titres_extraits:
                titre_extrait = titre_info_extrait["titre"]
                start_in_extrait = titre_info_extrait["debut"]+1
                end_in_extrait = titre_info_extrait["fin"]

                # Ajuster les positions du span dans l'extrait
                start_in_extrait_aligned, end_in_extrait_aligned = align_span_with_tokens(
                    start_in_extrait, end_in_extrait, doc_extrait
                )
                if start_in_extrait_aligned is None or end_in_extrait_aligned is None:
                    logger.debug(f"Impossible d'aligner le span dans l'extrait pour le titre : {titre_extrait}")
                    continue

                spans.append({
                    "text": titre_extrait,
                    "start": start_in_extrait_aligned,
                    "end": end_in_extrait_aligned,
                    "label": "TITRE"
                })

            if spans:
                extraits.append({
                    "text": extrait_autour_titre,
                    "spans": spans,
                    #"tokens": tokens_extrait,  
                    "meta": {"source": pdf_file}
                })
    nlp = None
    with open(chemin_sortie, 'w', encoding='utf-8') as f:
        for exemple in extraits:
            f.write(json.dumps(exemple, ensure_ascii=False) + '\n')

    logger.debug(f"JSONL pour Prodigy créé : {chemin_sortie} avec {len(extraits)} extraits.")