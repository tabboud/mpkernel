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

from pexpect import replwrap, EOF

# TODO: Get this from __init__.py
__version__ = '0.1'

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

    def run_command(self, command, timeout=30):
        """Run the python command """
        self.buffer = []
        self.output = ''
        try:
            # Replace the super call
            cmdlines = self._reconstruct_cmds(command.splitlines())
            self.child.sendline(cmdlines[0])
            for line in cmdlines[1:]:
                self._expect_prompt(timeout=1)
                self.child.sendline(line)

            # Command was fully submitted, now wait for the next prompt
            if self._expect_prompt(timeout=timeout) == 1:
                # We got the continuation prompt - command was incomplete
                self.child.kill(signal.SIGINT)
                self._expect_prompt(timeout=1)
                raise ValueError("Continuation prompt found - input was incomplete:\n" + command)
        finally:
            self.output = ''.join(self.buffer)
            self.buffer = []
        return self.output

    def _no_echo(self, buf):
        """Filter out input-echo"""
        store = False
        lines = []
        for line in buf.splitlines(True):
            if store:
                lines.append(line)
            elif '\r\n' == line:
                store = True
        return ''.join(lines)

    def _expect_prompt(self, timeout=30):
        x = ''
        try:
            x = self.child.expect_exact([self.prompt, '... '], timeout=timeout)
        finally:
            buf = self._no_echo(self.child.before)
            self.buffer.append(buf)
            return x

    def _reconstruct_cmds(self, lines):
        """Parse the commands and add in '' where neccesary

        Args:
            lines: lines that make up a command
        Returns:
            list of commands to run

        TODO: perform this in-place instead of making a new array
        """
        # iterate 1 time to see if there are any continuation blocks
        # if not, then just return the command lines
        # assume we dont have to change the commands
        change = False
        for cmd in lines:
            if cmd.endswith(':'):
                change = True
                break
        if change is False:
            lines.append('')
            return lines
        new_cmdlines = []
        parsing_continuation = False
        for cmd in lines:
            if cmd.endswith(':') or (cmd.startswith(' ') and parsing_continuation is True):
                parsing_continuation = True
                new_cmdlines.append(cmd)
            else:
                new_cmdlines.append('')
                new_cmdlines.append(cmd)
                parsing_continuation = False
        new_cmdlines.append('')
        return new_cmdlines


class MPKernelUnix(Kernel):
    """ Kernel for the Unix Port of micropython

    """
    # Required variables
    implementation = 'mpkernel'
    implementation_version = __version__
    banner = 'MPKernelUnix Banner'
    language_info = {
                    'name': 'micropython',
                    'codemirror_mode': 'python',
                    'mimetype': 'text/x-python',
                    'file_extension': '.py'
                    }
    micropython_exe = os.environ.get('MPUNIX')

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        # The path to the unix micropython should be in the PATH, if not check
        # the env for MPUNIX
        #TODO: Use shutil.which() in python 3.3+
        self.micropython_exe = 'micropython'
        if os.environ.get('MPUNIX') is not None:
            self.micropython_exe = os.environ.get('MPUNIX')

        self._start_interpreter()

    def _start_interpreter(self):
        # Signal handlers are inherited by forked processes, we can't easily
        # reset it from the subprocess. Kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler
        # so that bash and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            self.interpreter = MPUnixInterpreter(self.micropython_exe)
        finally:
            signal.signal(signal.SIGINT, sig)
        # self.language_version = self.interpreter.child.before.str

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
            output = self.interpreter.run_command(code, timeout=5)
        except KeyboardInterrupt:
            self.interpreter.child.sendintr()
            status = 'interrupted'
            self.interpreter._expect_prompt()
            output = self.interpreter.output
        except ValueError:
            output = self.interpreter.output + 'Incomplete input, restarting'
            self._start_interpreter()
        except EOF:
            output = self.interpreter.output + ' Restarting MPKernelUnix'
            self._start_interpreter()
        except EOF:
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
