""" Launch MPKernelStmhal """
try:
    from ipykernel.kernelapp import IPKernelApp
except ImportError:
    from IPython.kernel.zmq.kernelapp import IPKernelApp

from .stmhal import MPKernelStmhal

# Launch the pyboard port
IPKernelApp.launch_instance(kernel_class=MPKernelStmhal)

