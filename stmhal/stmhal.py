"""
stmhal.py

Jupyter kernel for the stmhal port of micropython

Notes:
    - The following must be run prior to any micropython code
        $ import sys!!
        $ sys.path.append('<path_to>/micropython/tools')!!
        $ import pyboard!!
        $ pyb = pyboard.Pyboard('<tty_device>')!!
    - The '!!' is how you run commands with the python 3 interpreter
        in Jupyter/Ipython. Any commands run without '!!' will be sent
        to the pyboard for processing
"""
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
__version__ = '0.2'

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
            newCodeStr = 'pyb.exec_raw(command="""{}""", timeout=None)'.format(newlines)

        # return super(MPKernelStmhal, self).do_execute(newCodeStr, silent, store_history, user_expressions, allow_stdin)

        # TODO: fetch return code here and parse it out, then return
        self._output = super(MPKernelStmhal, self).do_execute(newCodeStr, silent, store_history, user_expressions, allow_stdin)
        return self._output


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    # Launch the pyboard port
    IPKernelApp.launch_instance(kernel_class=MPKernelStmhal)

