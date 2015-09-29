#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import signal
from tornado.ioloop import IOLoop

try:
    from ipykernel.kernelbase import Kernel
except ImportError:
    from IPython.kernel.zmq.kernelbase import Kernel

from ipykernel.ipkernel import IPythonKernel

# TODO: Get this from __init__.py
__version__ = '0.1'

try:
    from traitlets import Unicode
except ImportError:
    from IPython.utils.traitlets import Unicode


class MPKernelStmhal(IPythonKernel):
    """ This subclasses the ipython kernel instead of
        wrapping around the kernel base, since we only
        need to alter the commands thats it runs
    """
    # Required variables
    implementation = 'mpkernel'
    implementation_version = __version__
    banner = 'MPKernelStmhal Banner'
    language_info = {
                    'name': 'micropython',
                    'codemirror_mode': 'python',
                    'mimetype': 'text/x-python',
                    'file_extension': '.py'
                    }

    def __init__(self, **kwargs):
        super(MPKernelStmhal, self).__init__(**kwargs)
        self._output = None
        # Need to run this code to setup the notebook  for us
        # setup_code = "import sys\nsys.path.append('/Users/User/dev/micropython/tools')\nimport pyboard\npyb = pyboard.Pyboard('/dev/tty.usbmodem1422')\n"
        # super(MPKernelStmhal, self).do_execute(setup_code, silent=True)

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        """
        TODO:
            - run multiline commands -> use docstring notation when running 
                the commands since it preserves the '\n'
            - run eval and exec commands (i.e. be able to print and just run 1+2)
            - parse the output correctly (utf-8 encoded -> 'string'.decode("utf-8"))
            - catch the exceptions (pyboard error)
            - handle different quotation marks
            - Figure out a way to connect to the device / setup paths
            - Figure out a better way to talk to main python
        """
        if '!!' in code:
            # allows us to enter a command and not send it to the board
            newCodeStr = code.replace('!!', '')
        else:
            lines = code.splitlines()
            newlines = '\n'.join(lines)
            newCodeStr = 'pyb.exec_("""{}""")'.format(newlines)

        # return super(MPKernelStmhal, self).do_execute(newCodeStr, silent, store_history, user_expressions, allow_stdin)

        # TODO: fetch return code here and parse it out, then return
        self._output = super(MPKernelStmhal, self).do_execute(newCodeStr, silent, store_history, user_expressions, allow_stdin)
        return self._output
