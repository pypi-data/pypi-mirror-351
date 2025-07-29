import time
import logging


from lxf.settings import get_logging_level

logger = logging.getLogger('Measures')
fh = logging.FileHandler('./logs/Measures.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)

def measure_time(func) :
    def inner(*arg,**kwargs):
        t=time.time()
        result = func(*arg,**kwargs)
        logger.debug(f"{func.__name__} executed in {(time.time()-t):.4f} seconds ")
        return result
    return inner

def  measure_time_async(func) :
    async def inner(*arg,**kwargs):
        t=time.time()
        result = await func(*arg,**kwargs)
        logger.debug(f"{func.__name__} executed in {(time.time()-t):.4f} seconds ")
        return result
    return inner


