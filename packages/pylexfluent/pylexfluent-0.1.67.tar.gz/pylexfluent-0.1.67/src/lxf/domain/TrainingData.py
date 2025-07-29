import logging
import lxf.settings as settings
settings.enable_tqdm=False
logger = logging.getLogger('Training Data')
fh = logging.FileHandler('./logs/training_data.log')
fh.setLevel(settings.get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(settings.get_logging_level())
logger.addHandler(fh)
from lxf.domain.entity import Entity

class DocumentTrainingData(Entity):
    def __init__(self,dictionary:dict=None) :
        if dictionary==None:
            super().__init__(sid="",parent_id="")
            self.name=""
            self.model=""
            self.famille=""
            self.category=""
            self.sub_category=""
            self.key_words={}
            self.key_phrases={}
        else :
            super().__init__(sid=dictionary["sid"],parent_id=dictionary["parent_id"])
            self.name=dictionary["name"]
            self.model=dictionary["model"]
            self.famille=dictionary["famille"]
            self.category=dictionary["category"]
            self.sub_category=dictionary["sub_category"]
            self.key_words = dictionary["key_words"]
            self.key_phrases=dictionary["key_phrases"]            
        

    def __str__(self)->str:
        return f"{DocumentTrainingData.__name__}\n{Entity.__str__(self)}\nclassification: {self.famille}_{self.category}_{self.sub_category}\nkey_words:{self.key_words}\nkey_phrases:{self.key_phrases}"
 