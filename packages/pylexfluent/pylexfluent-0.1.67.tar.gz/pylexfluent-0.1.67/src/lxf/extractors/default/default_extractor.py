#######################################

import logging

from tqdm import tqdm

from lxf.settings import get_logging_level, enable_tqdm
logger = logging.getLogger('default extractor')
fh = logging.FileHandler('./logs/default_extractor.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)
########################################


from lxf.ai.text_analysis.default_text_analysis import  decouper_text_par_titres, summarize_chunks

from lxf.domain.extracted_data import HIERARCHIE_DOCUMENT, HIERARCHIE_DOSSIER, Chunk, ChunkMetadata, ExtractedData, ExtractedMetadata
from lxf.domain.keyswordsandphrases import KeysWordsAndPhrases


def default_chunks_extractor(text: str,**kwargs) -> ExtractedData|None:
    """
    Effectue la segmentation et la reconnaissance d'entités nommées sur un texte donné.
    """    
    try:    
        if text == None :
            logging.error("Le texte fourni est vide")
            return None
        results:list[dict[str, str]] =decouper_text_par_titres(text)
        
        # for chunk in results :
        #     print(print_color.BLUE+f"\nTitre: {chunk["titre"]}")
        #     print(print_color.CYAN+f"Content : \n{chunk["contenu"]}")        

        source=kwargs.get("source","texte")
        if results == None: 
            logging.error("Aucun découpage de texte .")
            return  None
        extracted_data = ExtractedData()
        extracted_data.metadata=ExtractedMetadata()
        extracted_data.explain=f"""
Pour extraire des données du document ({source}), j'ai procédé selon les étapes suivantes:
 1) Découpage du texte par parties connues
 2) Extraction du texte contenu entre chaque partie
 3) Pour chaque texte extrait, identification des mots clés et génération d'un résumé
 4) Enfin, génération d'un résumé de la totalité du document et identification des mots clés pertinents
        
     
        """
        extracted_data.chunks=[]
        nb:int = len(results) +1
        default_summary=""
        # chunking des extraits de texte
        for i, chunk_dict in tqdm(enumerate(results),desc="Traitement des extraits obtenus",disable=not enable_tqdm,nrows=len(results),colour="BLUE"):
            try :
                chunk = Chunk()
                chunk.metadata = ChunkMetadata()
                chunk.metadata.chunk=i + 1
                chunk.metadata.chunks=nb
                chunk.metadata.title=chunk_dict.get("titre","extrait")      
                chunk.metadata.source=source        
                chunk.metadata.hierarchie = HIERARCHIE_DOCUMENT
                chunk.page_content = f"{chunk.metadata.title}\n{chunk_dict.get('contenu','')}  "
                next_title=""
                if i==nb-2 :
                    next_title = "la fin du document"
                else :
                    next_title=results[i+1].get("titre","le début la partie suivante")
                chunk.metadata.description = f"Extrait de texte compris entre {chunk.metadata.title} et {next_title}"
                # Calculer le résumer et les mots clés
                chunk_summaries=""
                if len(chunk.page_content)>30 :                 
                    tmp = summarize_chunks(chunk.page_content,summary_max_length=2048) 
                    chunk_summaries = "".join(tmp)
                else :
                    chunk_summaries = chunk.page_content            
                chunk.summary = chunk_summaries
                kw_process=KeysWordsAndPhrases(chunk.summary)
                if kw_process :
                    keywords=kw_process.get_key_words(threshold=0.2)
                    chunk.keywords=[key for key in keywords]
                # Explications
                chunk.explain=f"""
    Cet extrait a été produit par l'extraction du texte avant :{chunk.metadata.title} et {next_title}.
    Ensuite il y a eu identification des mots clés pertinents pour cet extrait.
    Pour finir, un résumé a été généré.           
                """
                extracted_data.chunks.append(chunk)

                default_summary+=f"{chunk_dict.get("titre",f"extrait {i+1}")}\n{chunk.summary}\n\n"
            except Exception as ex: 
                logger.critical(f"Exception :\n{ex}")
        try :
            # Ajout du résumé 
            global_summary=default_summary
            # chunk_summaries = summarize_chunks(default_summary,summary_max_length=4192)             
            # if chunk_summaries!=None and len(chunk_summaries)>0 :
            #     global_summary = "".join(chunk_summaries)  
            # calcul les mots clé depuis le résumé
            keysw = KeysWordsAndPhrases(global_summary)        
            keywords = keysw.get_key_words()
            if keywords :
                extracted_data.keywords=[key for key in keywords]                
            chunk = Chunk()
            chunk.metadata = ChunkMetadata()
            chunk.metadata.chunk = nb
            chunk.metadata.chunks = nb
            chunk.metadata.hierarchie = HIERARCHIE_DOSSIER        
            chunk.metadata.source =source    
            chunk.metadata.title="Résumé"
            chunk.metadata.description="Résumé du document"
            chunk.page_content=global_summary
            chunk.explain=f"""
    Cette partie est un résumé de toutes les parties précédantes.
    Ensuite il y a une identification des tous les mots clés pertinents.    
            """
            extracted_data.chunks.append(chunk)
        except Exception as ex: 
            logger.critical(f"Exception résumé final:\n{ex}")
    except Exception as e:
            logging.error(f"Erreur lors de la generation du resume global pour {source}.\nException : {e}")
            return None
    return extracted_data
