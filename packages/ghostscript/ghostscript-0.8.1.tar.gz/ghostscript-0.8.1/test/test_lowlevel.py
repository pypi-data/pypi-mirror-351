# -*- coding: utf-8 -*-
#
# This file is part of python-ghostscript.
# Copyright 2010-2023 by Hartmut Goebel <h.goebel@crazy-compilers.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "Copyright 2010-2023 by Hartmut Goebel <h.goebel@crazy-compilers.com>"
__licence__ = "GNU General Public License version 3 (GPL v3)"

import io
import locale # required to encode arguments
import binascii
import pathlib

import pytest

import ghostscript._gsprint as gs


HELLO_WORLD = ''.join(('%x' % ord(c) for c in 'Hello World'))
#HELLO_WORLD = binascii.hexlify('Hello World')
postscript_doc = ('<%s> = flush' % HELLO_WORLD).encode('ascii')

# For the low-level interface arguments have to be bytes. Encode them
# using local encoding to save calling set_arg_encoding().
STDARGS = [b'test.py', b'-dNOPAUSE', b'-dBATCH', b'-dSAFER', b'-q',
           b'-sDEVICE=bmp16', b'-g80x20']

POSTSCRIPT_FILE = pathlib.Path(__file__).with_name('testimage.ps')
POSTSCRIPT_DATA = POSTSCRIPT_FILE.read_bytes()
TEST_PIC = POSTSCRIPT_FILE.with_suffix('.bmp')
TEST_PIC_DATA = TEST_PIC.read_bytes()


def _encode(*args):
    # For the low-level interface arguments have to be bytes. Encode
    # them using local encoding to save calling set_arg_encoding().
    encoding = locale.getpreferredencoding()
    return [a.encode(encoding) for a in args]


def test_revision():
    rev = gs.revision()
    assert type(rev.copyright) is bytes
    assert type(rev.product) is bytes
    assert type(rev.revision) is int
    assert type(rev.revisiondate) is int


def test_run_string(tmpdir):
    """Let ghostscript read from a file and write to stdout"""
    outfile = tmpdir.join('out.bmp')

    args = STDARGS + _encode('-sOutputFile=%s' % outfile)

    instance = gs.new_instance()

    try:
        assert gs.init_with_args(instance, args) == 0
        assert gs.run_string(instance, POSTSCRIPT_DATA) == 0
    finally:
        gs.exit(instance)
        gs.delete_instance(instance)

    data = outfile.read('rb')
    assert data == TEST_PIC_DATA


def test_run_bugyy_string(tmpdir):
    """
    Test whether the program flow (try/finally, gs.exit,
    gs.delete_instance) is correct if executing fails.
    """
    args = STDARGS
    instance = gs.new_instance()
    try:
        assert gs.init_with_args(instance, args) == 0
        with pytest.raises(gs.GhostscriptError):
            gs.run_string(instance, b"invalid postscript code")
    finally:
        gs.exit(instance)
        gs.delete_instance(instance)


def test_simple(tmpdir):
    """Let ghostscript read from a file and write to a file"""
    infile = tmpdir.join('in.ps')
    infile.write(POSTSCRIPT_DATA)
    outfile = tmpdir.join('out.bmp')

    args = STDARGS + _encode('-sOutputFile=%s' % outfile, str(infile))

    instance = gs.new_instance()
    try:
        assert gs.init_with_args(instance, args) == 0
    finally:
        gs.exit(instance)
        gs.delete_instance(instance)

    data = outfile.read('rb')
    assert data == TEST_PIC_DATA


def _gs_stdio(args, stdin=None, stdout=None, stderr=None):
    instance = gs.new_instance()

    # wrappers like in
    # https://ghostscript.readthedocs.io/en/gs10.0.0/API.html#Example_usage
    if stdin  is not None: stdin  = gs._wrap_stdin(stdin)
    if stdout is not None: stdout = gs._wrap_stdout(stdout)
    if stderr is not None: stderr = gs._wrap_stderr(stderr)

    gs.set_stdio(instance, stdin, stdout, stderr)
    try:
        assert gs.init_with_args(instance, args) in (0, gs.e_Info)
    except gs.GhostscriptError as e:
        if e.code != gs.e_Quit:
            raise
    finally:
        gs.exit(instance)
        gs.delete_instance(instance)


def test_stdin(tmpdir):
    """Let ghostscript read from stdin and write to a file"""
    outfile = tmpdir.join('out.bmp')

    args = STDARGS + _encode('-sOutputFile=%s' % outfile, '-')

    _gs_stdio(args, stdin=io.BytesIO(POSTSCRIPT_DATA))

    data = outfile.read('rb')
    assert data == TEST_PIC_DATA


def test_stdout(tmpdir):
    """Let ghostscript read from a file and write to stdout"""
    infile = tmpdir.join('in.ps')
    infile.write(postscript_doc)

    args = STDARGS + _encode(str(infile))

    stdout = io.BytesIO() # buffer for collecting the output

    _gs_stdio(args, stdout=stdout)

    data = stdout.getvalue()
    assert data == b'Hello World\n'


def test_stdin_stdout(tmpdir):
    """Let ghostscript read from stdin and write to stdout"""
    args = STDARGS + _encode('-')

    stdout = io.BytesIO() # buffer for collecting the output

    _gs_stdio(args, stdin=io.BytesIO(postscript_doc), stdout=stdout)

    data = stdout.getvalue()
    assert data == b'Hello World\n'


def test_stderr(tmpdir):
    """
    Make ghostscript write some error message to stderr and
    keep stdout on the console.
    """
    args = STDARGS + _encode('-')

    stderr = io.BytesIO() # buffer for collecting stderr

    with pytest.raises(gs.GhostscriptError):
        # this call is expected to fail due to the intended error in
        # the postscript code
        _gs_stdio(args, stdin=io.BytesIO(b'foobar'), stderr=stderr)

    data = stderr.getvalue()
    assert b'Unrecoverable error' in data


def test_stdout_stderr(tmpdir):
    """
    Make ghostscript write some error message to stderr and
    catch stdout, too.
    """
    args = STDARGS + _encode('-')

    stdout = io.BytesIO() # buffer for collecting the output
    stderr = io.BytesIO() # buffer for collecting stderr

    with pytest.raises(gs.GhostscriptError):
        # this call is expected to fail due to the intended error in
        # the postscript code
        _gs_stdio(args,
                  stdin=io.BytesIO(b'foobar'), stdout=stdout, stderr=stderr)

    data = stdout.getvalue()
    assert b'Error: /undefined in foobar' in data

    data = stderr.getvalue()
    assert b'Unrecoverable error' in data



def generate_test_picture():
    """
    Use command line ghostscript to generate the image used in testing
    """
    import subprocess
    args = ['gs'] + STDARGS[1:] + _encode('-sOutputFile=%s' % TEST_PIC,
                                          str(POSTSCRIPT_FILE))
    subprocess.Popen(args).wait()


if __name__ ==  '__main__':
    generate_test_picture()
