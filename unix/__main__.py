""" Launch MPKernelUnix """
try:
    from ipykernel.kernelapp import IPKernelApp
except ImportError:
    from IPython.kernel.zmq.kernelapp import IPKernelApp

from .unix import MPKernelUnix

# Launch the unix port
IPKernelApp.launch_instance(kernel_class=MPKernelUnix)
