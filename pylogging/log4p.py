'''
A drop-in replacement to Python's logging framework.
Will correctly determine the fully qualified name of the logging event.

@author: Reggie Quimosing
'''

import inspect
from logging import handlers, config
import logging
import os
import sys

from . import get_full_filepath

root_level = logging.DEBUG

class Log4p(logging.Logger):
    '''
    Subclass of Logger that overrides the _log function so that the qualified name is 
    correctly determined, even when logging as __main__
    '''
    def __init__(self, name, level=logging.NOTSET):
        if name == '__main__':
            name = self.fully_qualified_module_name(4)
        super(Log4p, self).__init__(name, level)

    def _log(self, level, msg, args, exc_info=None, extra=None):
        """
        Low-level logging routine which creates a LogRecord and then calls
        all the handlers of this logger to handle the record.
        """
        if logging._srcfile:
            #IronPython doesn't track Python frames, so findCaller raises an
            #exception on some versions of IronPython. We trap it here so that
            #IronPython can use logging.
            try:
                qualified_name, fn, lno, func = self.fully_qualified_name(3)
            except ValueError:
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        else:
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        if exc_info:
            if not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = self.makeRecord(qualified_name, level, fn, lno, msg, args, exc_info, func, extra)
        self.handle(record)

    def fully_qualified_module_name(self, skip):
        """
        Get the fully qualified module name of a caller
 
        `skip` specifies how many levels of stack to skip while getting caller
        name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.
 
        An empty string is returned if skipped levels exceed stack height
        """
        stack = inspect.stack()
        start = 0 + skip
        if len(stack) < start + 1:
            return ''
        parentframe = stack[start][0]
        name = []
        module = inspect.getmodule(parentframe)
        # `modname` can be None when frame is executed directly in console
        # TODO(techtonik): consider using __main__
        if module:
            module_name = module.__name__
            if module_name == '__main__':                
                package_path = os.path.dirname(module.__file__)
                for path in sys.path:
                    if path in package_path and len(path) < len(package_path):
                        package_name = package_path.replace(path, '').replace('/', '.')[1:]
                        module_name = inspect.getmodulename(module.__file__)
                        name.append(package_name)
                        break
                if module_name == '__main__':
                    name.append(os.path.basename(package_path))
                    module_name = inspect.getmodulename(module.__file__)
            name.append(module_name)
        del parentframe
        return ".".join(name)

    def fully_qualified_name(self, skip):
        """
        Get a name of a caller in the format module.class.method
 
        `skip` specifies how many levels of stack to skip while getting caller
        name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.
 
        An empty string is returned if skipped levels exceed stack height
        """
        stack = inspect.stack()
        start = 0 + skip
        if len(stack) < start + 1:
            return ''
        parentframe = stack[start][0]
        name = []
        name.append(self.name)
        # detect classname
        if 'self' in parentframe.f_locals:
            # I don't know any way to detect call from the object method
            # XXX: there seems to be no way to detect static method call - it will
            #      be just a function call
            name.append(parentframe.f_locals['self'].__class__.__name__)
        codename = parentframe.f_code.co_name
#         if codename != '<module>':  # top level usually
#             name.append( codename ) # function or a method
        del parentframe
        return ".".join(name), stack[start][1], stack[start][2], codename

def get(name=None):
    '''
    Returns logger. If name is None, return the root logger.
    '''
    if name:
        return Log4p.manager.getLogger(name)
    else:
        return root

logging.setLoggerClass(Log4p)
if Log4p.root:
    root = Log4p.root
else:
    root = Log4p('root')
for h in root.handlers[:]:
    root.removeHandler(h)
    h.close()
Log4p.root = root
Log4p.manager = logging.Manager(Log4p.root)
Log4p.manager.setLoggerClass(Log4p)
logging.Logger.manager = Log4p.manager
logging.Logger.root = Log4p.root
root.setLevel(root_level)
logging.addLevelName(logging.WARNING, 'WARN')

# load config properties and initialize root logger
if not root.handlers:
    log_dir = os.getenv('LOGGING_DIRECTORY')
    if log_dir is not None:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    log_config = ''
    try:
        log_config = get_full_filepath('logging.config')
        config.fileConfig(log_config)
        get(__name__).info('Using config properties: ' + log_config)
        for logger_name, logger_obj in Log4p.manager.loggerDict.items():
            # rollover the file
            if isinstance(logger_obj, logging.Logger):
                for handler in logger_obj.handlers:
                    if isinstance(handler, handlers.TimedRotatingFileHandler):
                        print(handler.baseFilename)
                        handler.doRollover()
    except Exception as e:
        # formatter
        formatter = logging.Formatter('%(asctime)s.%(msecs)d000 %(levelname)s %(name)s.%(funcName)s:%(lineno)d [%(threadName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        # handlers
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(formatter)
        # add the handlers to the logger
        root.addHandler(stream_handler)
        get(__name__).debug('Failed to parse log config: %s' % log_config)
        get(__name__).debug('ERROR: %s' % str(e), exc_info=True)
        get(__name__).info('Using DEFAULT config properties in %s.' % inspect.getmodulename(__file__))
