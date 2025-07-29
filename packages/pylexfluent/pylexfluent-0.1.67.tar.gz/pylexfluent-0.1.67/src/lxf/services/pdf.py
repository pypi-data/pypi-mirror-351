import logging
from multiprocessing import Lock, Process, Queue
from lxf.settings import get_logging_level

#logger
logger = logging.getLogger('PDF services')
fh = logging.FileHandler('./logs/pdf_services.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)

import re
from typing import List

from tqdm import tqdm
from lxf.services.measure_time import measure_time, measure_time_async
from lxf.settings import enable_tqdm
from lxf.domain.tables import lxfCell, lxfRow, lxfTable


import pdfplumber

lock=Lock()

def sanitize_text(text:str)->str :
    temp_text=""
    last_char=" "
    try :
        if text==None or text == "" : return ""
        text=text.replace("–","-").replace("’","'").replace("\n"," ").replace("\"","'").replace('§','').strip()  
        regex = r"([A-Za-z]) ([A-Za-z]) "
        subst = r"\g<1>\g<2>" 
        text = re.sub(regex, subst, text)
        # remove extra space
        regex = r" {2,}"
        subst = " "
        # You can manually specify the number of replacements by changing the 4th argument
        return re.sub(regex, subst, text, 0, re.MULTILINE | re.DOTALL)    
    except Exception as ex:
            logger.exception(f"Exception occured in sanitize_text: {ex}")
    return temp_text 

def prune_text(text):

    def replace_cid(match):
        ascii_num = int(match.group(1))
        try:
            return chr(ascii_num)
        except:
            return ''  # In case of conversion failure, return empty string

    # Regular expression to find all (cid:x) patterns
    cid_pattern = re.compile(r'\(cid:(\d+)\)')
    pruned_text = re.sub(cid_pattern, replace_cid, text)
    return pruned_text

@measure_time_async
async def get_text_from_pdf(filename:str,max_pages:int=-1) :
    """
    Extrait le texte contenu dans un pdf
    filename: le nom du fichier pdf
    """
    with pdfplumber.open(filename,laparams={"detect_vertical": False}) as pdf:
        text =''
        if max_pages>0 :
            pages_to_read = pdf.pages[:max_pages]
        else :
            pages_to_read = pdf.pages
        for page in pages_to_read :
            words = page.extract_words(x_tolerance=1,y_tolerance=1, use_text_flow=True, line_dir="ltr")       
            if not words==None :
                for word in words:
                    text = text + " "+word['text']          
        pdf.close()
        return sanitize_text(text)

@measure_time_async
async def get_text_and_tables_from_pdf_wwith_mp(filename:str,extract_tables:bool=True,max_pages:int=-1)->tuple[str,List[lxfTable]|None] :
    """
    """
    with lock :
        queue:Queue=Queue()
        p:Process=Process(target=get_text_and_tables_from_pdf_mp,args=(filename,extract_tables,max_pages,queue))
        p.start()
        p.join()
        result:tuple[str,List[lxfTable]|None] = queue.get()
        if result !=None :
            return result
        else :
            logger.warning(f"{filename} aucun texte ou table trouve")
            return "", None

@measure_time
def get_text_and_tables_from_pdf_mp(filename:str,extract_tables:bool,max_pages:int,queue:Queue)->tuple[str,List[lxfTable]|None] :
    """
    Extrait tout le text et toutes les tables contenues dans un pdf
    filename: le nom du fichier pdf
    return: text , lxfPages 
    """
    DEFAULT_SNAP_TOLERANCE = 3
    DEFAULT_JOIN_TOLERANCE = 3
    DEFAULT_MIN_WORDS_VERTICAL = 3
    DEFAULT_MIN_WORDS_HORIZONTAL = 1
    DEFAULT_TABLE_SETTINGS = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "explicit_vertical_lines": [],
    "explicit_horizontal_lines": [],
    "snap_tolerance": DEFAULT_SNAP_TOLERANCE,
    "join_tolerance": DEFAULT_JOIN_TOLERANCE,
    "edge_min_length": 3,
    "min_words_vertical": DEFAULT_MIN_WORDS_VERTICAL,
    "min_words_horizontal": DEFAULT_MIN_WORDS_HORIZONTAL,
    #"keep_blank_chars": False,
    "text_tolerance": 3,
    "text_x_tolerance": 3,
    "text_y_tolerance": 3,
    "intersection_tolerance": 3,
    "intersection_x_tolerance": 3,
    "intersection_y_tolerance": 3,
    }
    settings = dict(DEFAULT_TABLE_SETTINGS)
    settings["text_tolerance"]=1
    settings["text_x_tolerance"]=1
    settings["text_y_tolerance"]=1
 

    with pdfplumber.open(filename) as pdf:
        found_tables:List[lxfTable]=[]
        index_table=0
        text=""
        unicode_dash=re.compile(r'\xad')
        if max_pages>0 :
            pages_to_read = pdf.pages[:max_pages]
        else :
            pages_to_read = pdf.pages
        for page_number, page in tqdm(enumerate(pages_to_read,start=1),desc=f"{filename}: Lecture page en cours ",disable= not enable_tqdm):
            #Get Text
            t = page.extract_text(x_tolerance=1,y_tolerance=5)
            if not t==None :
                if 'cid' in t :
                    t = prune_text(t)
                # Gérer les cas où les tirets sont en unicode \xad 
                elif '\xad' in t :
                    t=re.sub(unicode_dash,'-',t)                    
                text = text + t   
            #Get Tables within the current page
            tables=None
            if extract_tables :
                tables = page.extract_tables(settings)
                if not tables==None and not len(tables)==0:  
                    for table in tables:
                        index_table+=1                    
                        lxf_table=lxfTable()
                        lxf_table.page_number = page_number
                        #lxf_table.number = index_table
                        for row in table :
                            if not row== None:
                                lxf_row=lxfRow()
                                for cell in row :
                                    if not (cell == None or cell==" "):
                                        lxf_cell=lxfCell()
                                        if 'cid' in cell :
                                            cell = prune_text(cell)
                                        # Gérer les cas où les tirets sont en unicode \xad 
                                        elif '\xad' in t :
                                            t=re.sub(unicode_dash,'-',t)  
                                        lxf_cell.value =sanitize_text(cell)
                                        lxf_row.cells.append(lxf_cell)                                        
                                lxf_table.rows.append(lxf_row)                                                         
                        found_tables.append(lxf_table)
        pdf.close()
        result:tuple[str,List[lxfTable]|None] = text, found_tables
        queue.put(result)

READ_ERROR_SPACES_IN_WORD=1
def detect_read_error(text:str)->int :
    """
    """
    # regex = r"[^ \n\-']{26,}"
    regex = r"([A-Za-z] [A-Za-z] ){2,}"
    matches = re.findall(regex, text, re.MULTILINE)
    result= matches!=None and len(matches)>0
    error =0 
    if result : 
        logger.warning(f"Erreur de lecture detectee : {matches[:3]}")
        error=READ_ERROR_SPACES_IN_WORD
    return error

@measure_time_async
async def get_text_and_tables_from_pdf(filename:str,extract_text:bool=True,extract_tables:bool=True,layout:bool=False,max_pages:int=-1)->tuple[str,List[lxfTable]|None] :
    """
    Extrait tout le text et toutes les tables contenues dans un pdf
    filename: le nom du fichier pdf
    return: text , lxfPages 
    """
    DEFAULT_SNAP_TOLERANCE = 3
    DEFAULT_JOIN_TOLERANCE = 3
    DEFAULT_MIN_WORDS_VERTICAL = 3
    DEFAULT_MIN_WORDS_HORIZONTAL = 1
    DEFAULT_TABLE_SETTINGS = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "explicit_vertical_lines": [],
    "explicit_horizontal_lines": [],
    "snap_tolerance": DEFAULT_SNAP_TOLERANCE,
    "join_tolerance": DEFAULT_JOIN_TOLERANCE,
    "edge_min_length": 3,
    "min_words_vertical": DEFAULT_MIN_WORDS_VERTICAL,
    "min_words_horizontal": DEFAULT_MIN_WORDS_HORIZONTAL,
    #"keep_blank_chars": False,
    "text_tolerance": 3,
    "text_x_tolerance": 3,
    "text_y_tolerance": 3,
    "intersection_tolerance": 3,
    "intersection_x_tolerance": 3,
    "intersection_y_tolerance": 3,
    }
    settings = dict(DEFAULT_TABLE_SETTINGS)
    settings["text_tolerance"]=1
    settings["text_x_tolerance"]=1
    settings["text_y_tolerance"]=1
 

    with pdfplumber.open(filename) as pdf:
        found_tables:List[lxfTable]=[]
        index_table=0
        text=""
        unicode_dash=re.compile(r'\xad')
        if max_pages>0 :
            pages_to_read = pdf.pages[:max_pages]
        else :
            pages_to_read = pdf.pages
        for page_number, page in tqdm(enumerate(pages_to_read,start=1),desc=f"{filename}: Lecture page en cours ",disable= not enable_tqdm):
            #Get Text
            if extract_text :
                t = page.extract_text(x_tolerance=2,y_tolerance=5, layout=layout)
                if detect_read_error(t)==READ_ERROR_SPACES_IN_WORD : 
                    t = page.extract_text(x_tolerance=5,y_tolerance=5,layout=layout)            
                if not t==None :
                    if 'cid' in t :
                        t = prune_text(t)
                    # Gérer les cas où les tirets sont en unicode \xad 
                    elif '\xad' in t :
                        t=re.sub(unicode_dash,'-',t)                    
                    text = text + t   
            #Get Tables within the current page
            tables=None
            if extract_tables :
                tables = page.extract_tables(settings)
                if not tables==None and not len(tables)==0:  
                    for table in tables:
                        index_table+=1                    
                        lxf_table=lxfTable()
                        lxf_table.page_number = page_number
                        #lxf_table.number = index_table
                        for row in table :
                            if not row== None:
                                lxf_row=lxfRow()
                                for cell in row :
                                    if not (cell == None or cell==" "):
                                        lxf_cell=lxfCell()
                                        if 'cid' in cell :
                                            cell = prune_text(cell)
                                        # Gérer les cas où les tirets sont en unicode \xad 
                                        elif '\xad' in cell :
                                            t=re.sub(unicode_dash,'-',t)  
                                        lxf_cell.value =sanitize_text(cell)
                                        lxf_row.cells.append(lxf_cell)                                        
                                lxf_table.rows.append(lxf_row)                                                         
                        found_tables.append(lxf_table)
        pdf.close()
        result:tuple[str,List[lxfTable]|None] = text, found_tables
        return result