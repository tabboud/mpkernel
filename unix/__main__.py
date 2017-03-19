""" Launch MPKernelUnix """
from ipykernel.kernelapp import IPKernelApp
from .unix import MPKernelUnix

# Launch the unix port
IPKernelApp.launch_instance(kernel_class=MPKernelUnix)

