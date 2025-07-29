import datetime
import os
import logging
from lxf.settings import get_logging_level, nlp_with_vectors
###################################################################
logger = logging.getLogger('repertoire_extractor')
fh = logging.FileHandler('./logs/repertoire_extractor.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)
#################################################################



from lxf.domain.predictions import Predictions
from lxf.ai.text_analysis.default_text_analysis import summarize_chunks
from lxf.domain.keyswordsandphrases import KeysWordsAndPhrases
from lxf.domain.extracted_data import HIERARCHIE_DOCUMENT, HIERARCHIE_REPERTOIRE, Chunk, ChunkMetadata, ExtractedData, ExtractedMetadata
from lxf.domain.tables import lxfRow, lxfTable
from lxf.ai.classification.classifier import extract_text_and_table_from_file
from lxf.utilities.tables_helper import reconciliation_tables 
from lxf.domain.repertoire import Nature, RepertoireNotaire
from lxf.utilities.text_comparator import TextComparator
from dateutil.parser import parse




def consolidate_tables(tables:list[lxfTable]) -> list[lxfTable] :
    """
    il peut y avoir des enregistrements de répertoire sur plusieurs lignes dans la colonne Répertoire
    ce n'est pas acceptable, il faut fusionner avec la ligne précédente les lignes qui n'ont pas de numéro de répertoire
    ni date de signature mais du texte pour répertoire    
    """
    consolided_tables:list[lxfTable]=[]
    for table in tables : 
        consolided_table:lxfTable=lxfTable()
        previous_row:lxfRow = table.rows[0]
        # Toujours ajouter l'entête cad la première ligne
        consolided_table.rows.append(previous_row)
        for row in table.rows[1:] : 
            num_rep=row.cells[0].value
            if num_rep==None : num_rep=""
            date_sign=row.cells[1].value
            if date_sign==None : date_sign=""
            text=row.cells[3].value
            if text==None : text=""                    
            if num_rep.strip()=="" and date_sign.strip()=="" and text.strip()!="":
                # Il faut fusioner le text avec la ligne précédente
                previous_row.cells[3].value+=text
            else :
                if num_rep!="" and date_sign!="" and text!="" :
                    # Ajouter cette ligne
                    consolided_table.rows.append(row)
                    previous_row=row
        # ajouter la table consolidée
        consolided_tables.append(consolided_table)  
    return consolided_tables  

def extract_repertoires_from_tables(tables:list[lxfTable])->list[RepertoireNotaire]:
    """
    Retrouver les champs RepertoireNotaire dans la table en fonction de l'entête de la table
    """
    # Définition des outils de comparaison pour retrouver le mapping des champs
    num_rep_comparator:TextComparator=TextComparator("N°Répert.",nlp_with_vectors)
    signature_compator:TextComparator=TextComparator("Signature",nlp_with_vectors)
    brevet_minute_comparator:TextComparator=TextComparator("B/M",nlp_with_vectors)
    repertoire_comparator:TextComparator=TextComparator("Répertoire",nlp_with_vectors)
    support_comparator:TextComparator=TextComparator("Support",nlp_with_vectors)
    date_formalite_comparator:TextComparator=TextComparator("Date de formalité",nlp_with_vectors)
    depot_comparator:TextComparator=TextComparator("Dépôt", nlp_with_vectors)
    percu_comparator:TextComparator=TextComparator('Perçu',nlp_with_vectors)
    dt_etat_comparator:TextComparator=TextComparator("Dt sur Etat")
    visa:TextComparator=TextComparator("Visa",nlp_with_vectors)
    num_clerc_comparator:TextComparator=TextComparator("Numéro Clerc")
    # Clés pour le mapping des champs
    NUM_REP="num_rep"
    SIGNATURE="signature"
    BREVET_MINUTE="brevet_minute"
    TEXT="text"
    SUPPORT="support"
    DATE_FORMALITE="date_form"
    DEPOT="depot"
    PERCU="percu"
    DT_ETAT="dt_etat"
    VISA="visa"
    NUM_CLERC="num_clerc"   
     
    repertoires:list[RepertoireNotaire]=[]
    for table in tables:
        # Récupérer l'entête
        entete:list[str] = [cell.value for cell in table.rows[0].cells]
        # Retrouver le mapping des champs par rapport à l'entête
        mapping_fields:dict=dict()        
        for i,key in enumerate(entete) : 
            if num_rep_comparator.compare_to(key) >0.85 :
                mapping_fields[NUM_REP]=i
            elif signature_compator.compare_to(key)>0.85 :
                mapping_fields[SIGNATURE]=i
            elif brevet_minute_comparator.compare_to(key)>0.85 :
                mapping_fields[BREVET_MINUTE]=i                    
            elif repertoire_comparator.compare_to(key)>0.85 :
                mapping_fields[TEXT]=i                        
            elif support_comparator.compare_to(key)>0.85 :
                mapping_fields[SUPPORT]=i 
            elif date_formalite_comparator.compare_to(key)>0.85 :
                mapping_fields[DATE_FORMALITE]=i 
            elif depot_comparator.compare_to(key)>0.85 :
                mapping_fields[DEPOT]=i     
            elif percu_comparator.compare_to(key)>0.85 :
                mapping_fields[PERCU]=i       
            elif dt_etat_comparator.compare_to(key)>0.85 :
                mapping_fields[DT_ETAT]=i    
            elif visa.compare_to(key)>0.85 :
                mapping_fields[VISA]=i          
            elif num_clerc_comparator.compare_to(key)>0.85 :
                mapping_fields[NUM_CLERC]=i                                                                                                             
        # Mapping retrouvé
        # Mapper les champs en fonction de l'entête
        for row in table.rows[1:] : 
            # Le numéro de répertoire est obligatoire
            if row.cells[mapping_fields[NUM_REP]].value.strip()=="" : 
                logger.warning("Un enregistrement n'a pas de numéro de répertoire, il a été ignoré")
            else:                   
                rep:RepertoireNotaire=RepertoireNotaire()
                rep.num_repertoire = row.cells[mapping_fields[NUM_REP]].value
                rep.date_signature=row.cells[mapping_fields[SIGNATURE]].value
                b_m=row.cells[mapping_fields[BREVET_MINUTE]].value
                if b_m.lower()=="m" : rep.nature=Nature.Minute
                else : rep.nature = Nature.Brevet
                rep.text = row.cells[mapping_fields[TEXT]].value
                rep.support=row.cells[mapping_fields[SUPPORT]].value
                rep.date_formalite=row.cells[mapping_fields[DATE_FORMALITE]].value
                rep.depot=row.cells[mapping_fields[DEPOT]].value
                rep.droit_sur_etat=row.cells[mapping_fields[DT_ETAT]].value
                rep.visa=row.cells[mapping_fields[VISA]].value
                num_clerc:str= row.cells[mapping_fields[NUM_CLERC]].value
                tmp= num_clerc.split(" ")
                rep.numero_acte =tmp[0]
                rep.clerc=tmp[1]
                repertoires.append(rep)
    return repertoires

def get_extractedData_from_repertoires(repertoires:list[RepertoireNotaire],documentId:str, source:str,predictions:Predictions=Predictions()) -> ExtractedData :
    """
    Converti la liste des répertoires en ExtractedData
    """
    extracteData:ExtractedData=ExtractedData()
    extracteData.metadata = ExtractedMetadata()
    extracteData.metadata.origine="GeDAIA"
    extracteData.metadata.documentId=documentId
    extracteData.metadata.traite_le = datetime.datetime.today().strftime('%d/%m/%Y %H:%M')
    extracteData.keywords=["Répertoire","Minute","Brevet","Date Signature", "Date Formalité","Numéro répertoire", "Numéro d'acte","Support AAE","Support papier"]
    # Données de classification
    extracteData.metadata.classe=predictions.BestPrediction
    extracteData.metadata.classe_confidence=predictions.BestPredictionConfidence
    extracteData.explain="Ces données ont été extraites du répertoire de l'office depuis des documents PDF"      
    
    extracteData.chunks=[]
    for repertoire in repertoires : 
        chunk:Chunk=Chunk()
        chunk.metadata=ChunkMetadata()
        chunk.metadata.chunk=1
        chunk.metadata.chunks=1
        chunk.metadata.title = repertoire.text.split(":")[0][:80]
        chunk.metadata.source=source
        chunk.metadata.extra_metadata["Classification"]=predictions.BestPrediction
        chunk.metadata.extra_metadata["Classification confiance"]=predictions.BestPredictionConfidence
        try:
            if repertoire.date_signature!=None and repertoire.date_signature!="":
                chunk.metadata.extra_metadata["date_signature"]=parse(repertoire.date_signature)
            if repertoire.date_formalite!=None and repertoire.date_formalite.strip()!="":
                chunk.metadata.extra_metadata["date_formalite"]=parse(repertoire.date_formalite)
        except Exception as ex:
            logger.critical(f"Tentative de conversion en date\nSignature={repertoire.date_signature}\nFormalite={repertoire.date_formalite}\nException: {ex}",stack_info=True)
        chunk.metadata.extra_metadata["num_rep"]=repertoire.num_repertoire    
        chunk.metadata.extra_metadata["nature"]=repertoire.nature
        chunk.metadata.extra_metadata["support"]=repertoire.support
        chunk.metadata.extra_metadata["num_acte"]=repertoire.numero_acte        
        chunk.metadata.extra_metadata["initiales_clerc"]=repertoire.clerc
        # Il s'agit du répertoire
        chunk.metadata.hierarchie=HIERARCHIE_REPERTOIRE
        
        
        chunk.page_content =f"""
Numéro de répertoire : {repertoire.num_repertoire}
Date de Signature : {repertoire.date_signature}
Nature : {repertoire.nature}
Texte:
{repertoire.text}
Support : {repertoire.support}
Date Formalité : {repertoire.date_formalite}
Dépôt : {repertoire.depot}
Perçu : {repertoire.frais_percus}
Droit sur Etat: {repertoire.droit_sur_etat}
Visa : {repertoire.visa}
Numéro acte dans la rédaction : {repertoire.numero_acte}
Initiales Clerc : {repertoire.clerc}        
        """ 
        
        # if len(repertoire.text)> 30 :
        #     tmp = summarize_chunks(repertoire.text[:1024]) 
        #     chunk_summaries = "".join(tmp)
        # else : 
        #     chunk_summaries=repertoire.text
        chunk.summary=repertoire.text[:256]        
        #chunk.summary=repertoire.text.split(":")[0]
        chunk.explain="Ces données ont été extraites du répertoire de l'office depuis des documents PDF"        
        kw_process=KeysWordsAndPhrases(chunk.page_content)
        if kw_process :
            keywords=kw_process.get_key_words(threshold=0.3)
            chunk.keywords=[key for key in keywords]                
        extracteData.chunks.append(chunk)
    return extracteData    
        
    
async def extract_repertoire_data(file_path:str,**kwargs)->tuple[int,str,ExtractedData|None]:
    """
    Extraction des données du répertoire contenu dans le fichier 
    """
    if file_path==None or file_path=="": 
        err_msg:str= "Argument vide ou None!"
        logging.error(err_msg,stack_info=True)
        return -2,err_msg, None
    if os.path.isfile(file_path) ==False :
        err_msg:str=f"Le fichier {file_path} n'existe pas!"
        logging.error(err_msg, stack_info=True)
        return -3, err_msg,None
    documentId:str=kwargs.get("documentId","")
    predictions:Predictions = kwargs.get("predictions",Predictions())
    try: 
        tables:list[lxfTable] 
        # Rechercher d'abord dans les tableaux s'il y en a 
        _,tables = await extract_text_and_table_from_file(file_name=file_path,layout=True,extract_tables=True, extract_text=False)
        if tables!=None :     
            err, err_msg, merged_tables = reconciliation_tables(tables)
            if err<0 :
                #Erreur 
                err_msg:str=f"Reconciliation des tableaux erreur : {err} - {err_msg}"
                logging.error(err_msg)
                return -4, err_msg, None                  
            # il peut y avoir des enregistrements de répertoire sur plusieurs lignes dans la colonne Répertoire
            # ce n'est pas acceptable, il faut fusionner avec la ligne précédente les lignes qui n'ont pas de numéro de répertoire
            # ni date de signature mais du texte pour répertoire
            consolided_tables = consolidate_tables(merged_tables)    
            repertoires:list[RepertoireNotaire] = extract_repertoires_from_tables(consolided_tables)
            if len(repertoires)==0 :
                return -4 , "Aucun répertoire extrait", None
            data:ExtractedData = get_extractedData_from_repertoires(repertoires,documentId, file_path, predictions)
            if data!=None :                 
                return 0, "", data
            else :
                logger.error(f"La conversion en ExtractedData a échouée",stack_info=True)
                return -10, "La conversion en ExtractedData a échouée"
    except Exception as excep:
        err_msg:str = f"Une erreur critique est apparue:\n{excep}"
        logging.critical(err_msg,stack_info=True)
        return -1, err_msg, None