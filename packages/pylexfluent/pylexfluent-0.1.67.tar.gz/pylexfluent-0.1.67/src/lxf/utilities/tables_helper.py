import logging

import tqdm
from lxf.settings import get_logging_level, nlp_with_vectors, enable_tqdm

#logger
logger = logging.getLogger('Tables Helper')
fh = logging.FileHandler('./logs/tables_helper.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)

from lxf.domain.tables import lxfTables, lxfTable
from lxf.utilities.text_comparator import TextArrayComparator

def reconciliation_tables(tables:list[lxfTable])-> tuple[int, str,list[lxfTable]|None]:
    """
    Reconcilent plusieurs tables consécutives qui ont le même entête (cad 1 ligne de la table)
    """
    
    # Vérifications
    if tables==None or len (tables)==0 :
        return -100 , "Tables ne peut pas vide", None
    entete_courante = [cell.value for cell in tables[0].rows[0].cells]
    entete_comparator:TextArrayComparator=TextArrayComparator(entete_courante,nlp_with_vectors)
    merged_tables:list[lxfTable]= []
    table_courrante:lxfTable=lxfTable()
    # initialisation avec la première ligne (entete) du premier tableau
    table_courrante.rows.append(tables[0].rows[0])
    for table in tqdm.tqdm(tables,desc="Lecture des tables",disable=not enable_tqdm) :
        entete_a_verifier = [cell.value for cell in table.rows[0].cells]
        if entete_comparator.compare_to(entete_a_verifier)<0.85 : 
            # ce n'est pas la même entête, c'est donc un nouveau tableau
            # ajouter le tableau 
            merged_tables.append(table_courrante)
            # nouvelle table courrante
            table_courrante = lxfTable
            table_courrante.rows.append(table.rows[0])
            # nouvelle entête
            entete_courante = entete_a_verifier
            # Nouvelle entête comparator
            entete_comparator=None 
            entete_comparator=TextArrayComparator(entete_courante,nlp_with_vectors)            
        # il faut ajouter toutes les lignes suivantes de 1 à len(table) -1
        for row in table.rows[1:] : 
            table_courrante.rows.append(row)   
    if len(table_courrante.rows)>0: 
        merged_tables.append(table_courrante)
    return 0 , "", merged_tables
    
    
            
