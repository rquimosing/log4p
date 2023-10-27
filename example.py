'''
Created on Oct 23, 2023

@author: rquimosing
'''

import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.info('Hello World')

from pylogging import log4p

logger = log4p.get(__name__)
logger.info('Hello World')