.. image:: https://travis-ci.org/TDAbboud/mpkernel.svg?branch=master
    :target: https://travis-ci.org/TDAbboud/mpkernel

mpkernel
========
Jupyter/IPython kernels for micropython

WARNING:
    This is still very early in development so things may break!

Requirements
============
* Python 3.4+
* Jupyter  >= 1.0.0 (install with pip)
* pyserial >= 2.7   (install with pip)
 
Installation
============

Make sure you have the packages under requirements installed then run the following::

    $ git clone https://github.com/TDAbboud/mpkernel.git
    $ cd mpkernel
    $ make install

.. Future pip installation
    The easiest way to install mpkernel is with pip::

    $ pip install mpkernel

    This will install kernels for the unix (`mpunix`) and stmhal(`mpstmhal`) port

    See its `Python Package Index entry`_ for more.


Unix port
---------
You must add micropython to the environments PATH variable::
        
    $ export PATH="<path_to>/micropython/unix:$PATH"

Alternatively, you can set the following environment variable::

    $ export MPUNIX=<path_to>/micropython/unix

Stmhal port
------------
You need to run some setup boilerplate code before you can run any micropython
code, see the examples directory::

    $ import sys!!
    $ sys.path.append('<path_to>/micropython/tools')!!
    $ import pyboard!!
    $ pyb = pyboard.Pyboard('<tty_device>')!!

The '!!' is how you run commands with the python 3 interpreter in Jupyter/Ipython. Any commands run without '!!' will be sent to the pyboard for processing

Usage
=====
start the notebook server::

    $ jupyter notebook

select either micropython-unix or micropython-stmhal from the drop down menu  
or
run either kernel from the console::

    $ jupyter console --kernel=mpunix
    $ jupyter console --kernel=mpstmhal

Vagrant
=======
run vagrant up from within this repository to create a mpkernel development
environment, with the latest micropython build

Contributing
============
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am "Add some feature"`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D


License
=======
The MIT License (MIT)

Copyright (c) 2015 Tony Abboud

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


.. _Python Package Index entry: http://pypi.python.org/pypi/mpkernel
