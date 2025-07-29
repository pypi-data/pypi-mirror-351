import logging
import os
from typing import List 
from lxf.ai.text_analysis.default_text_analysis import summarize_chunks
from lxf.settings import get_logging_level
###################################################################

logger = logging.getLogger('Loan2ExtractedData')
fh = logging.FileHandler('./logs/loan2extracteddata.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)
#################################################################

from lxf.domain.loan import Assurance, Emprunteur, Pret, ProgrammeFinancier, Warranty
from dotenv import dotenv_values
from lxf.services.measure_time import measure_time

from lxf.domain.extracted_data import HIERARCHIE_DOSSIER, Chunk, ChunkMetadata, ExtractedData, ExtractedMetadata
from lxf.domain.predictions import Predictions


def get_metatata(entity_id:str, pret:Pret, p:Predictions)->ExtractedMetadata:
    metadata = ExtractedMetadata()
    metadata.origine = "Ingestion/Offre de prêt"
    metadata.classe = p.BestPrediction
    metadata.classe_confidence= p.BestPredictionConfidence
    metadata.documentId = entity_id

    return metadata

def get_common_section(pret:Pret)->str:
    return f"""
        Information de suivi et de gestion du dossier de prêt
        Numéro de suivi : {pret.num_suivi} 
        Offre : {pret.header_offre} 
        Référence de l'offre : {pret.header_ref} 
        Responsable du suivi de l'offre: {pret.header_responsable_suivi} 
        Numéro Etude : {pret.header_num_etude}                                
        Date d'émission de l'offre : {pret.date_emission_offre} 
    """ 

def get_section_objet_du_financement(pret:Pret)->str :
        
    def get_programme_financier(p:ProgrammeFinancier) -> str:
        msg=""
        for ele in p.plan_financement :  
            msg+=f"""
                  {ele.nature} : {ele.montant.valeur} {ele.montant.devise}
            """
        msg+=f"""
        Montant du Programme : {p.montant_programme.valeur} {p.montant_programme.devise}
        """
        return msg

    msg = f"""
    """
    nb_financement= len (pret.objets_financement)
    for index,financement in enumerate(pret.objets_financement) :
        msg+=f"""  
    Plan de financement avec l'objet et la nature du prêt        
    Financement {index+1}/{nb_financement}   
    Objet du financement : {financement.titre}
    Nature du prêt: {financement.nature}
    Adresse : {financement.adresse} {financement.code_postal} {financement.ville}
    Description complète: 
                {financement.description} 
        """
    msg+=f"""
    PLAN FINANCEMENT :
    {get_programme_financier(pret.programme_financier)}
    """
    msg+="""
    """
    return msg

def get_section_preteur(pret:Pret)->str :
                
    return f"""
        Information sur la banque prêteuse du prêt   
                          
                          
        Nom de la banque : {pret.preteur.raison_sociale}
        Statut de la banque: {pret.preteur.statut_organisation}
        Adresse de la banque : {pret.preteur.adresse} {pret.preteur.code_postal} {pret.preteur.ville}
        SIREN/SIRET : {pret.preteur.siren} {pret.preteur.siret}
    """    

def get_section_emprunteurs(pret:Pret)-> str :
    emprunteurs:List[Emprunteur] = pret.emprunteurs
    section_emprunteurs =f"""
    Liste des emprunteurs et de leur représentant     
    Prêt    
    """
    i=0
    for emprunteur in emprunteurs :
        i+=1
        section_emprunteurs+=f"""
        Emprunteur :
        """
        if emprunteur.est_personne ==False:

            section_emprunteurs+=f"""
            Raison sociale :{emprunteur.raison_sociale}
            Statut : {emprunteur.statut_organisation}
            Siren/Siret: {emprunteur.siren} {emprunteur.siret}
            Adresse : {emprunteur.adresse} {emprunteur.code_postal} {emprunteur.ville}
                """
            for representant in emprunteur.represente_par :
                section_emprunteurs+=f"""
            Représenté par :
                Nom : {representant.civilite} {representant.prenoms} {representant.nom}
                Né(e) le : {representant.date_naissance}
                Situation maritale : {representant.situation_maritale}
                Métier : {representant.metier}
                Adresse : {representant.adresse} {representant.code_postal} {representant.ville}
                    """
        else :
            section_emprunteurs+=f"""
            Nom : {emprunteur.civilite} {emprunteur.prenoms} {emprunteur.nom}
            Né(e) le : {emprunteur.date_naissance}
            Situation maritale : {emprunteur.situation_maritale}
            Métier : {emprunteur.metier}
            Adresse : {emprunteur.adresse} {emprunteur.code_postal} {emprunteur.ville}            
                """
            for representant in emprunteur.represente_par :
                section_emprunteurs+=f"""
            Représenté par :
                Nom : {representant.civilite} {representant.prenoms} {representant.nom}
                Né(e) le : {representant.date_naissance}
                Situation maritale : {representant.situation_maritale}
                Métier : {representant.metier}
                Adresse : {representant.adresse} {representant.code_postal} {representant.ville}
                    """    
     
    return section_emprunteurs + """
    """

def get_list_des_prets(p:Pret)->str :
    msg="""
     Liste des prêts avec leur numéro et montant     
    """
    msg+="_"*70
    msg+="""    
    |{nature:30}|{numero:^18}|{montant:18}|
    """.format(nature="Nature",numero="numero",montant="Montant")
    msg+="="*70
    for ele in p.list_prets :
        msg+="""
    |{nature:30}|{numero:^18}|{valeur:<14} {devise:>3}|
    """.format(nature=ele.nature[:30],numero=ele.numero,valeur=ele.montant.valeur, devise=ele.montant.devise[:3])
    msg+="_"*70
    msg+="""
    
    """
    return msg

def get_caracteristiques_pret(p:Pret)->str :
    msg="""
    Caractéristiques du prêt    
    """
    for caract in p.caracteristiques_prets :
        msg+=f"""
        Prêt: {caract.description} 
        Numéro : {caract.numero_pret}
        Montant total : {caract.montant}
        Domiciliation :
            Débiteur: {caract.domiciliation.debiteur} 
            Compte : {caract.domiciliation.compte}
            Créancier: {caract.domiciliation.creancier}        
        Taux : {caract.taux.description}. Pourcentage: {caract.taux.taux_pourcentage}% Période : {caract.taux.taux_periode}.  Base période: {caract.taux.base_periode}.
        Montant total crédit: {caract.montant_total_du_emprunteurs.cout_total_credit.valeur} {caract.montant_total_du_emprunteurs.cout_total_credit.devise}
        Montant total des intérêts : {caract.montant_total_du_emprunteurs.montant_total_interets.valeur} {caract.montant_total_du_emprunteurs.montant_total_interets.devise}
        Montant total assurances obligatoires : {caract.montant_total_du_emprunteurs.montant_total_assurance_obligatoire.valeur} {caract.montant_total_du_emprunteurs.montant_total_assurance_obligatoire.devise}       
        """
        for frais in caract.montant_total_du_emprunteurs.frais :
            msg+=f"""
            - {frais.nature}: {frais.montant.valeur} {frais.montant.devise}"""            
        msg+=f"""
        Montant total dû emprunteur : {caract.montant_total_du_emprunteurs.montant_total_credit.valeur} {caract.montant_total_du_emprunteurs.montant_total_credit.devise}
        """
        for periode in caract.periodes_amortissement : 
            msg+=f"""
            Type d'échéance : {periode.type_echeance}
            Durée échéances : {periode.duree_echeances}
            Périodicité échéance : {periode.periodicite_echeance}
            Type de taux débiteur: {periode.type_taux_debiteur}
            Taux débiteur : {periode.taux_debiteur_pourcentage}%
            Montant des échéances :
            """
            for montant in periode.montant_echeances:
                msg+=f"""
                {montant.txt_montant}: {montant.montant.valeur} {montant.montant.devise}
                """
            msg+=f"""
            Assurance : {periode.assurance.valeur} {periode.assurance.devise}
            Accessoire: {periode.accessoire.valeur} {periode.accessoire.devise}
            """
    msg+="""
    
    """
    return msg

def get_assurances(p:Pret)->str:
    assurances:list[Assurance] = p.assurances
    msg="""
     Liste des assurances du prêt et des souscripteurs    
    """
    for assurance in assurances : 
        msg+=f"""
        Souscripteur Assuré(e) : {assurance.souscripteur}
            Référence : {assurance.reference}
            Délégation : {assurance.delegation}
            
                Nom de naissance : {assurance.nom_naissance_souscripteur}
                Date de naissance : {assurance.date_naissance_souscripteur}
                Ville de naissance : {assurance.ville_naissance_souscripteur}
            Garanties prises: {assurance.garanties}
            Assureur : {assurance.assureur}
            Type assureur : {assurance.type_assureur}
            Groupe assureur : {assurance.assureur_group}
            Quotité prêt assuré : {assurance.quotite_pret_assure}
            Options choisies : {assurance.options_choisies}
            Hauteur pourcentage : {assurance.hauteur_pourcentage}
            Couverture : {assurance.couverture}
            Tableau des prêts        
        """
        table_prets = assurance.tableau_prets
        msg+="\n"
        nb_rows = len(table_prets.rows)
        for irow, row in enumerate(table_prets.rows):            
            for cell in row.cells :
                msg+=f" {cell.value:40}|"
            # sauter une ligne 
            msg+="\n"            
            if irow+1<nb_rows :
                # une séparation sauf pour la dernière ligne
                for cell in row.cells :
                    msg+="="*42            
                # sauter une ligne 
                msg+="\n"            

        # msg+=f"""
        #     Description complète:

        #         {assurance.description}
            
        #     """
        msg+=f"""
        
        """
    msg+="""
    
    """
    return msg

def get_garanties(p:Pret)->str :
    
    garanties:list[Warranty] = p.garanties
    msg=f"""
    Liste des garanties du prêt 
    """
    for garantie in garanties:
        msg+=f"""
        Garantie : {garantie.label}
        Rang: {garantie.rang}
        Hauteur : {garantie.hauteur}
        Numéro du prêt : {garantie.numero_pret}
        Références cadastrales : {garantie.ref_cadastrales}
            Adresse : {garantie.adresse_immeuble_cadastre}
            Code postal : {garantie.code_poste_immeuble_cadastre}
            Ville : {garantie.ville_immeuble_cadatre}
        Notaire :
            Office : {garantie.office_notarial}
            Addresse : {garantie.adresse_office_notarial}
            Code postal : {garantie.code_postal_office_notarial}
            Ville : {garantie.ville_office_notarial}
        Durée : {garantie.duree} {garantie.duree_unite}
        Durée limitée : {garantie.duree_limitee} {garantie.duree_limitee_unite}
        """
    return msg

def get_clauses_particulieres(p:Pret)->str:
    if len(p.clauses_particulieres)==0 : return "Aucune CLAUSE PARTICULIERE"
    msg="""    
    Liste des clauses particulières du prêt
    """
    for clause in p.clauses_particulieres:
        msg+=f"""
        Titre : {clause.titre}
        Numéro prêt: {clause.numero_pret}
        Texte de la clause :
        {clause.text}

        """
    msg+="""
    -------------
    """
    return msg

def get_tableau_ammortissement(p:Pret)->str:
    if p.tableau_amortissement==None or len(p.tableau_amortissement.rows)==0 :
        return "Pas de tableau d'amortissement"    
    msg="""
    TABLEAU AMORTISSEMENT

    """
    msg+="\n"  
    table_amortissement = p.tableau_amortissement
    nb_rows = len(table_amortissement.rows)
    for irow, row in enumerate(table_amortissement.rows):            
        for cell in row.cells :
            msg+=f" {cell.value:30}|"
        # sauter une ligne 
        msg+="\n"            
        if irow+1<nb_rows :
            # une séparation sauf pour la dernière ligne
            for cell in row.cells :
                msg+="="*32            
            # sauter une ligne 
            msg+="\n"    
    msg+="""
    FIN TABLEAU AMORTISSEMENT
    """
    return msg

def get_summarization(p:Pret)->str:
    """
    Retourne un résumé du prêt
    """
    msg=f"""
    {get_common_section(p)}
    
    {get_section_preteur(p)}
    
    {get_section_emprunteurs(p)}
       
        Plan de financement avec l'objet et la nature du prêt
    """
    nb_financement= len (p.objets_financement)
    for index,financement in enumerate(p.objets_financement) :
        msg+=f"""  
                Financement {index+1}/{nb_financement}   
                Objet du financement : {financement.titre}
                Nature du prêt: {financement.nature}
        """
    msg+=f"""
    
    {get_list_des_prets(p)}
    
    Caractéristiques du prêt
    """
    for caract in p.caracteristiques_prets :
        msg+=f"""
            Prêt: {caract.description} 
            Numéro : {caract.numero_pret}
            Montant total : {caract.montant}
            Domiciliation :
                Débiteur: {caract.domiciliation.debiteur} 
                Compte : {caract.domiciliation.compte}
                Créancier: {caract.domiciliation.creancier}        
            Taux : {caract.taux.description}. Pourcentage: {caract.taux.taux_pourcentage}% Période : {caract.taux.taux_periode}.  Base période: {caract.taux.base_periode}.
            Montant total crédit: {caract.montant_total_du_emprunteurs.cout_total_credit.valeur} {caract.montant_total_du_emprunteurs.cout_total_credit.devise}
            Montant total des intérêts : {caract.montant_total_du_emprunteurs.montant_total_interets.valeur} {caract.montant_total_du_emprunteurs.montant_total_interets.devise}
            Montant total assurances obligatoires : {caract.montant_total_du_emprunteurs.montant_total_assurance_obligatoire.valeur} {caract.montant_total_du_emprunteurs.montant_total_assurance_obligatoire.devise}       
    """    

    msg+=f"""
    
    {get_assurances(p)}
    
    """
    msg+=f"""
    
    {get_garanties(p)}
    
    """
    return msg

@measure_time
def loan_to_extracted_data(pret:Pret,file_name:str, entity_id:str="-1",predictions:Predictions=Predictions())->tuple[int,ExtractedData,str] :
    """
    """
    try :
        
        if pret!=None:
            default_summary=""
            data=ExtractedData()
            nb_chunks:int=11                
            i_chunk:int=1
            data.metadata = get_metatata(entity_id=entity_id, pret=pret,p=predictions)
            chunk =Chunk()
            chunk.metadata=ChunkMetadata()
            chunk.metadata.chunk=i_chunk
            chunk.metadata.chunks=nb_chunks
            chunk.metadata.title="ENTETE"
            chunk.metadata.description="Entête du prêts"
            chunk.metadata.source=file_name
            chunk.page_content=get_common_section(pret)         
            chunk.summary = chunk.page_content
            # Explications
            chunk.explain=f"""
Cet extrait a été obtenu en extrayant l'entête de l'offre de prêt          
                """            
            default_summary+=f"{chunk.metadata.title}\n{chunk.summary}\n"
            data.chunks.append(chunk)
                            
            i_chunk+=1
            data.metadata = get_metatata(entity_id=entity_id, pret=pret,p=predictions)
            chunk =Chunk()
            chunk.metadata=ChunkMetadata()
            chunk.metadata.chunk=i_chunk
            chunk.metadata.chunks=nb_chunks
            chunk.metadata.title="PRETEUR"
            chunk.metadata.source=file_name                    
            chunk.metadata.description="Liste des prêteurs"
            chunk.page_content=get_section_preteur(pret)
            chunk.summary = chunk.page_content
            # Explications
            chunk.explain=f"""
Cet extrait a été obtenu en extrayant la liste des prêteurs          
                """            
            default_summary+=f"{chunk.metadata.title}\n{chunk.summary}\n"            
            data.chunks.append(chunk)
            
            i_chunk+=1
            chunk=Chunk()
            chunk.metadata=ChunkMetadata()
            chunk.metadata.chunk=i_chunk
            chunk.metadata.chunks=nb_chunks
            chunk.metadata.title="EMPRUNTEURS"
            chunk.metadata.description="Liste des emprunteurs"
            chunk.metadata.source=file_name
            chunk.page_content=get_section_emprunteurs(pret)
            # Calculer le résumer et les mots clés
            chunk_summaries = chunk.page_content            
            chunk.summary = chunk_summaries
            # Explications
            chunk.explain=f"""
Cet extrait a été obtenu en extrayant la liste des emprunteurs         
                """            
            default_summary+=f"{chunk.metadata.title}\n{chunk.summary}\n"            
            data.chunks.append(chunk)
            
            i_chunk+=1
            chunk=Chunk()
            chunk.metadata = ChunkMetadata()
            chunk.metadata.chunk=i_chunk
            chunk.metadata.chunks=nb_chunks
            chunk.metadata.title="OBJET des FINANCEMENTS"
            chunk.metadata.description="Objet de tous les financements"
            chunk.metadata.source=file_name
            chunk.page_content = get_section_objet_du_financement(pret)    
            chunk.summary = chunk.page_content
            # Explications
            chunk.explain=f"""
Cet extrait a été obtenu en extrayant l'objet(s) des/du financement(s)        
                """            
            default_summary+=f"{chunk.metadata.title}\n{chunk.summary}\n"            
            data.chunks.append(chunk)

            i_chunk+=1 
            chunk=Chunk()
            chunk.metadata=ChunkMetadata()
            chunk.metadata.chunk= i_chunk
            chunk.metadata.chunks=nb_chunks
            chunk.metadata.title="Liste des prêts"
            chunk.metadata.description="LISTE des PRETS"
            chunk.metadata.source=file_name
            chunk.page_content = get_list_des_prets(pret)         
            chunk.summary = chunk.page_content
            # Explications
            chunk.explain=f"""
Cet extrait a été obtenu en extrayant l'entête de l'offre de prêt          
                """            
            default_summary+=f"{chunk.metadata.title}\n{chunk.summary}\n"            
            data.chunks.append(chunk)

            i_chunk+=1 
            chunk=Chunk()
            chunk.metadata=ChunkMetadata()
            chunk.metadata.chunk= i_chunk
            chunk.metadata.chunks=nb_chunks
            chunk.metadata.title="Caractéristiques"
            chunk.metadata.description="Caractéristiques financiers des PRETS"
            chunk.metadata.source=file_name
            chunk.page_content = get_caracteristiques_pret(pret)       
            chunk.summary = chunk.page_content
            # Explications
            chunk.explain=f"""
Cet extrait a été obtenu en extrayant la liste des prêts         
                """            
            default_summary+=f"{chunk.metadata.title}\n{chunk.summary}\n"            
            data.chunks.append(chunk)

            i_chunk+=1 
            chunk=Chunk()
            chunk.metadata=ChunkMetadata()
            chunk.metadata.chunk= i_chunk
            chunk.metadata.chunks=nb_chunks
            chunk.metadata.title="Assurances"
            chunk.metadata.description="Liste des assurances souscrites"
            chunk.metadata.source=file_name
            chunk.page_content = get_assurances(pret)          
            chunk.summary = chunk.page_content
            # Explications
            chunk.explain=f"""
Cet extrait a été obtenu en extrayant la liste des assurances souscriptes par les emprunteurs         
                """            
            default_summary+=f"{chunk.metadata.title}\n{chunk.summary}\n"            
            data.chunks.append(chunk)

            i_chunk+=1 
            chunk=Chunk()
            chunk.metadata=ChunkMetadata()
            chunk.metadata.chunk= i_chunk
            chunk.metadata.chunks=nb_chunks
            chunk.metadata.title="Garanties"
            chunk.metadata.description="Liste des garanties prises"
            chunk.metadata.source=file_name
            chunk.page_content = get_garanties(pret)         
            chunk.summary = chunk.page_content
            # Explications
            chunk.explain=f"""
Cet extrait a été obtenu en extrayant la liste des emprunteurs       
                """            
            default_summary+=f"{chunk.metadata.title}\n{chunk.summary}\n"            
            data.chunks.append(chunk)

            i_chunk+=1 
            chunk=Chunk()
            chunk.metadata=ChunkMetadata()
            chunk.metadata.chunk= i_chunk
            chunk.metadata.chunks=nb_chunks
            chunk.metadata.title="Clauses particulières"
            chunk.metadata.description="Liste des clause particuluères"
            chunk.metadata.source=file_name
            chunk.page_content = get_clauses_particulieres(pret)
            # Calculer le résumer et les mots clés
            if len(chunk.page_content)>30 :                 
                tmp = summarize_chunks(chunk.page_content,summary_max_length=512) 
                chunk_summaries = "".join(tmp)
            else :
                chunk_summaries = chunk.page_content            
            chunk.summary = chunk_summaries
            # Explications
            chunk.explain=f"""
Cet extrait a été obtenu en extrayant la liste des clauses particulières          
                """            
            default_summary+=f"{chunk.metadata.title}\n{chunk.summary}\n"            
            data.chunks.append(chunk)

            i_chunk+=1 
            chunk=Chunk()
            chunk.metadata=ChunkMetadata()
            chunk.metadata.chunk= i_chunk
            chunk.metadata.chunks=nb_chunks
            chunk.metadata.title="Tableau d'amortissement"
            chunk.metadata.description="Tableau des amortissement"
            chunk.metadata.source=file_name
            chunk.page_content = get_tableau_ammortissement(pret)          
            chunk.summary = chunk.page_content
            # Explications
            chunk.explain=f"""
Cet extrait a été obtenu en extrayant le tableau d'amortissement         
                """            
            # pour le résumé, on ne prend pas le tableau d'amortissement
            #default_summary+=f"{chunk.metadata.title}\n{chunk.summary}\n"
            data.chunks.append(chunk)
            
            i_chunk+=1 
            chunk=Chunk()
            chunk.metadata=ChunkMetadata()
            chunk.metadata.chunk= i_chunk
            chunk.metadata.chunks=nb_chunks
            chunk.metadata.title="Résumé"
            chunk.metadata.description="Résumé de l'offre de prêt"
            chunk.metadata.hierarchie=HIERARCHIE_DOSSIER
            chunk.metadata.source=file_name
            chunk.page_content =default_summary
            chunk.summary =  get_summarization(p=pret)     
            # Explications
            chunk.explain=f"""
Cet extrait a été obtenu en extrayant toutes les parties caractéristiques de l'offre de prêt         
                """            
            data.chunks.append(chunk)             
                    
            data.keywords.append("PRET")
            data.keywords.append("Bancaire")
            data.keywords.append("BPACA")
            data.keywords.append("PTZ")    
            data.keywords.append("GARANTIES")
            data.keywords.append("ASSURANCES")         
            
            return 0,data ,"sucess"  
    except Exception as ex: 
        err_msg=f"Exception dans Loan to_ExtractedData:\n{ex}"
        logger.critical(err_msg,stack_info=True)
        return -1,None, err_msg