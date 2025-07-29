import logging
import lxf.settings as settings
settings.enable_tqdm=False
logger = logging.getLogger('Entity')
fh = logging.FileHandler('./logs/entity.log')
fh.setLevel(settings.get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(settings.get_logging_level())
logger.addHandler(fh)

class Entity:
    def __init__(self,sid,parent_id):
        self.sid=sid
        self.parent_id=parent_id

    
    def __str__(self)->str:
        """
        """
        tmp:str=f"sid={self.sid} parent_id={self.parent_id}"
        logger.debug(tmp)
        return tmp