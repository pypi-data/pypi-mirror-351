
import logging
import lxf.settings as settings
logger = logging.getLogger('Train Repository')
fh = logging.FileHandler('./logs/train_repository.log')
fh.setLevel(settings.get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(settings.get_logging_level())
logger.addHandler(fh)
#####################################################

from datetime import datetime
from pytz import timezone
import uuid
import pymongo
from lxf.domain.entity import Entity
from lxf.services.measure_time import measure_time


europe_paris_tz=timezone("Europe/Paris")
class LexiaDb :
    def __init__(self,connection_string) :
        self.conn_str = connection_string
        self.client = pymongo.MongoClient(self.conn_str, serverSelectionTimeoutMS=30000)
        self.db = self.client.lexia
        try:
            logger.debug(self.client.server_info())
        except Exception as ex:
            logger.error(f"Exception occured : {ex}")
    
    def get_db(self) :
        return self.db

class Repository:
    
    @measure_time
    def __init__(self,lexia_db:LexiaDb,collection):
        self.db=lexia_db.db
        self.collection_name=collection
        self.collection=self.db[collection]
    
    @measure_time
    def insert(self,item:Entity)->Entity: 
        result:Entity=None
        try:
            item.sid=f"SID_{self.collection_name}_{uuid.uuid1()}"
            item.created_date=datetime.now(tz=europe_paris_tz)
            logger.debug(item)
            self.collection.insert_one(item.__dict__)
            result= item
        except Exception as ex:
            logger.critical(f"insert_one exception occured {ex}")
        return result
    
    @measure_time
    def insertOrUpdate(self,filter,item:Entity)->Entity:
        try :
            foundEntity = self.collection.find_one(filter)
            if foundEntity==None:                
                item_result=self.insert(item)
                return item_result
            else:
                item.sid = foundEntity['sid']
                logger.debug(f"Found {foundEntity} - Name={item.name} SID={item.sid}")                
                item.updated_date=datetime.now(tz=europe_paris_tz)
                item_result = item
                update_result=self.collection.update_one(filter,{'$set':item.__dict__},upsert=True)
                if update_result.modified_count>0 : return item_result
                else: return None

            
        except Exception as ex :
            logger.critical(f"insertOrUpdate failed {ex}\n Filter: {filter}\nValue:{item}")
            return False
    
    @measure_time
    def fine_one_by_filter(self, filter) -> Entity :
        return self.collection.find_one(filter)
    
    @measure_time
    def get_all(self):
        return self.collection.find()
    
    @measure_time
    def get_byfilter(self,filter):
        result=self.collection.find(filter)
        return result

class TrainingDataRepository(Repository):
    @measure_time
    def __init__(self,lexia_db:LexiaDb):
        super().__init__( lexia_db,TrainingDataRepository.__name__.replace("Repository",""))