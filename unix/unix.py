#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import signal
from tornado.ioloop import IOLoop
from ipykernel.kernelbase import Kernel
from pexpect import replwrap, EOF

__version__ = '0.2'

try:
    from traitlets import Unicode
except ImportError:
    from IPython.utils.traitlets import Unicode


class MPUnixInterpreter(replwrap.REPLWrapper):
    """
    Extension of replwrap to micropython for the unix port
    """
    def __init__(self, cmd, **kw):
        self.prompt = '>>> '
        self.buffer = []
        self.output = ''
        super(MPUnixInterpreter, self).__init__(cmd, self.prompt, None, **kw)

    def run_command(self, command, timeout=-1):
        """Send a command to the REPL, wait for and return output.

        :param str command: The command to send. Trailing newlines are not needed.
          This should be a complete block of input that will trigger execution;
          if a continuation prompt is found after sending input, :exc:`ValueError`
          will be raised.
        :param int timeout: How long to wait for the next prompt. -1 means the
          default from the :class:`pexpect.spawn` object (default 30 seconds).
          None means to wait indefinitely.
        """
        # Split up multiline commands and feed them in bit-by-bit
        cmdlines = [command]
        # splitlines ignores trailing newlines - add it back in manually
        if command.endswith('\n'):
            cmdlines.append('')
        if not cmdlines:
            raise ValueError("No command was given")

        res = []
        self.child.sendline(cmdlines[0])
        for line in cmdlines[1:]:
            self._expect_prompt(timeout=timeout)
            res.append(self.child.before)
            self.child.sendline(line)

        # Command was fully submitted, now wait for the next prompt
        if self._expect_prompt(timeout=timeout) == 1:
            # We got the continuation prompt - command was incomplete
            self.child.kill(signal.SIGINT)
            self._expect_prompt(timeout=1)
            raise ValueError("Continuation prompt found - input was incomplete:\n"
                             + command)
        return u''.join(res + [self.child.before])


class MPKernelUnix(Kernel):
    """
    Kernel for the Unix Port of micropython
    """
    implementation = 'mpkernel'
    implementation_version = __version__
    banner = 'Welcome to the Unix port of MicroPython'
    language_info = {
                    'name': 'micropython',
                    'version': '3',
                    'codemirror_mode': {
                            'name': 'python',
                            'version': 3
                        },
                    'mimetype': 'text/x-python',
                    'file_extension': '.py',
                    'pygments_lexer': 'python3',
                    }

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self.micropython_exe = 'micropython'
        self.start_interpreter()

    def start_interpreter(self):
        # Signal handlers are inherited by forked processes, we can't easily
        # reset it from the subprocess. Kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler
        # so that bash and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            self.interpreter = MPUnixInterpreter(self.micropython_exe)
        finally:
            signal.signal(signal.SIGINT, sig)

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):

        if not code.strip():
            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }

        status = 'ok'
        traceback = None

        try:
            # compile the code then run an exec of that code object
            compile_output = self.interpreter.run_command("c = compile({0!r}, 'mpkernel', 'exec')".format(code), timeout=5)
            if compile_output is not None:
                output = self.interpreter.run_command('exec(c)', timeout=5)
            else:
                raise Exception("Error in compile: ({})\n".format(compile_output))
        except KeyboardInterrupt:
            self.interpreter.child.sendintr()
            status = 'interrupted'
            self.interpreter._expect_prompt()
            output = self.interpreter.output
        except ValueError:
            output = self.interpreter.output + 'Incomplete input, restarting'
            self.start_interpreter()
        except EOF:
            output = self.interpreter.output + ' Restarting MPKernelUnix'
            self.start_interpreter()
            status = 'error'
            traceback = []

        if not self.interpreter.child.isalive():
            self.log.error("MPKernelUnix interpreter died")
            loop = IOLoop.current()
            loop.add_callback(loop.stop)

        if not silent:
            # Send output on stdout
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        reply = {
            'status': status,
            'execution_count': self.execution_count,
        }

        if status == 'interrupted':
            pass
        elif status == 'error':
            err = {
                'ename': 'ename',
                'evalue': 'evalue',
                'traceback': traceback,
            }
            self.send_response(self.iopub_socket, 'error', err)
            reply.update(err)
        elif status == 'ok':
            reply.update({
                'payload': [],
                'user_expressions': {},
            })
        else:
            raise ValueError("Invalid status: %r" % status)

        return reply

