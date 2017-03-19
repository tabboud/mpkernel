#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import sys
import os
import json
from setuptools import setup, find_packages
from distutils.command.install import install

# The package names
pkg_main = 'mpkernel'
pkg_unix = 'unix'
pkg_stmhal = 'stmhal'

# ----------------------------------------------------------------------------
# Configure the kernel json files
# ----------------------------------------------------------------------------
kernel_json_unix = {
    "display_name": "micropython-unix",
    "language": "python",
    "argv": [
        sys.executable,
        "-m",
        pkg_unix,
        "-f",
        "{connection_file}"
    ]
}

kernel_json_pyboard = {
    "display_name": "micropython-stmhal",
    "language": "python",
    "argv": [
        sys.executable,
        "-m",
        pkg_stmhal,
        "-f",
        "{connection_file}"
    ]
}


class install_with_kernelspec(install):
    def run(self):
        install.run(self)
        try:
            from jupyter_client.kernelspec import install_kernel_spec
        except ImportError:
            from IPython.kernel.kernelspec import install_kernel_spec
        from IPython.utils.tempdir import TemporaryDirectory

        # Install unix port
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755)
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json_unix, f, sort_keys=True)
            kernel_name = 'mp' + pkg_unix
            try:
                install_kernel_spec(td, kernel_name=kernel_name,
                                    user=self.user, replace=True)
            except:
                install_kernel_spec(td, kernel_name=kernel_name,
                                    user=not self.user, replace=True)

        # Install pyboard port
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755)
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json_pyboard, f, sort_keys=True)
            kernel_name = 'mp' + pkg_stmhal
            try:
                install_kernel_spec(td, kernel_name=kernel_name,
                                    user=self.user, replace=True)
            except:
                install_kernel_spec(td, kernel_name=kernel_name,
                                    user=not self.user, replace=True)

# TODO: The following prevents having to add --egg for pip install
# svem_flag = '--single-version-externally-managed'
# if svem_flag in sys.argv:
#     # Die, setuptools, die.
#     sys.argv.remove(svem_flag)

with open('README.md') as readme_file:
    readme = readme_file.read()


setup(
    name=pkg_main,
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    cmdclass={'install': install_with_kernelspec},
    test_suite='tests',
    tests_require=[
    ],
    install_requires=[
        'jupyter>=1.0.0',
        'pyserial>=2.7'
        ],

    # Metadata for PyPI
    author='Tony Abboud',
    author_email='tony.abboud54@gmail.com',
    description='Micropython Kernels for Jupyter/Ipython',
    long_description=readme,
    license='MIT',
    keywords=['Micropython', 'ipython', 'interactive'],
    # Project home page
    url='https://github.com/tdabboud/%s' % pkg_main,
    # download_url='https://github.com/tdabboud/%s/tarball/0.1' % pkg_main,
    platforms='Linux',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: MIT License'
        ]
)
