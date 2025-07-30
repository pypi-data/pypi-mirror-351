import logging
from typing import Dict

loggers: Dict[str, logging.Logger]

def getLogger(name:str,subFolder:str=None,backupCount:int=365) -> logging.Logger: ...
