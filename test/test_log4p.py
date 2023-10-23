'''
Created on Oct 17, 2023

@author: rquimosing
'''
import logging
import unittest
from unittest.mock import patch

from pylogging import log4p


class TestLog4p(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger = log4p.get(__name__)
        logger.info('Testing log4p')    

    def testRootLogger(self):
        logger = log4p.get()
        self.assertTrue(log4p.Log4p.root == logger)
        self.assertTrue(isinstance(logger, logging.RootLogger))

    @patch("pylogging.log4p.Log4p")
    def testDebug(self, mock_logger):
        logger = log4p.get('debug_logger')
        mock_logger.manager.getLogger().test_assert_called_with('debug_logger')
        logger.debug('test debug')
        mock_logger.manager.getLogger().debug().test_assert_called_with('test debug')

    @patch("pylogging.log4p.Log4p")
    def testInfo(self, mock_logger):
        logger = log4p.get('info_logger')
        mock_logger.manager.getLogger().test_assert_called_with('info_logger')
        logger.info('test info')
        mock_logger.manager.getLogger().info().test_assert_called_with('test info')

    @patch("pylogging.log4p.Log4p")
    def testWarn(self, mock_logger):
        logger = log4p.get('warn_logger')
        mock_logger.manager.getLogger().test_assert_called_with('warn_logger')
        logger.warn('test warn')
        mock_logger.manager.getLogger().warn().test_assert_called_with('test warn')

    @patch("pylogging.log4p.Log4p")
    def testError(self, mock_logger):
        logger = log4p.get('error_logger')
        mock_logger.manager.getLogger().test_assert_called_with('error_logger')
        logger.error('test error')
        mock_logger.manager.getLogger().error().test_assert_called_with('test error')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()