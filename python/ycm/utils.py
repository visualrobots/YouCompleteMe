#!/usr/bin/env python
#
# Copyright (C) 2011, 2012  Strahinja Val Markovic  <val@markovic.io>
#
# This file is part of YouCompleteMe.
#
# YouCompleteMe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YouCompleteMe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YouCompleteMe.  If not, see <http://www.gnu.org/licenses/>.

import tempfile
import os
import sys
import signal
import functools
import socket
import stat

WIN_PYTHON27_PATH = 'C:\python27\pythonw.exe'
WIN_PYTHON26_PATH = 'C:\python26\pythonw.exe'


def IsIdentifierChar( char ):
  return char.isalnum() or char == '_'


def SanitizeQuery( query ):
  return query.strip()


def ToUtf8IfNeeded( string_or_unicode ):
  if isinstance( string_or_unicode, unicode ):
    return string_or_unicode.encode( 'utf8' )
  return string_or_unicode


def PathToTempDir():
  tempdir = os.path.join( tempfile.gettempdir(), 'ycm_temp' )
  if not os.path.exists( tempdir ):
    os.makedirs( tempdir )
    # Needed to support multiple users working on the same machine;
    # see issue 606.
    MakeFolderAccessibleToAll( tempdir )
  return tempdir


def MakeFolderAccessibleToAll( path_to_folder ):
  current_stat = os.stat( path_to_folder )
  # readable, writable and executable by everyone
  flags = ( current_stat.st_mode | stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH
            | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP )
  os.chmod( path_to_folder, flags )


def GetUnusedLocalhostPort():
  sock = socket.socket()
  # This tells the OS to give us any free port in the range [1024 - 65535]
  sock.bind( ( '', 0 ) )
  port = sock.getsockname()[ 1 ]
  sock.close()
  return port


def PathToPythonInterpreter():
  # This is a bit tricky. Normally, sys.executable has the full path to the
  # Python interpreter. But this code is also executed from inside Vim's
  # embedded Python. On Unix machines, even that Python returns a good value for
  # sys.executable, but on Windows it returns the path to the Vim binary, which
  # is useless to us (issue #581). So we check the common install location for
  # Python on Windows, first for Python 2.7 and then for 2.6.
  #
  # I'm open to better ideas on how to do this.

  if OnWindows():
    if os.path.exists( WIN_PYTHON27_PATH ):
      return WIN_PYTHON27_PATH
    elif os.path.exists( WIN_PYTHON26_PATH ):
      return WIN_PYTHON26_PATH
    raise RuntimeError( 'Python 2.7/2.6 not installed!' )
  else:
    return sys.executable


def OnWindows():
  return sys.platform == 'win32'


# From here: http://stackoverflow.com/a/8536476/1672783
def TerminateProcess( pid ):
  if OnWindows():
    import ctypes
    PROCESS_TERMINATE = 1
    handle = ctypes.windll.kernel32.OpenProcess( PROCESS_TERMINATE,
                                                 False,
                                                 pid )
    ctypes.windll.kernel32.TerminateProcess( handle, -1 )
    ctypes.windll.kernel32.CloseHandle( handle )
  else:
    os.kill( pid, signal.SIGTERM )


def AddThirdPartyFoldersToSysPath():
  path_to_third_party = os.path.join(
                          os.path.dirname( os.path.abspath( __file__ ) ),
                          '../../third_party' )

  for folder in os.listdir( path_to_third_party ):
    sys.path.insert( 0, os.path.realpath( os.path.join( path_to_third_party,
                                                        folder ) ) )

def Memoize( obj ):
  cache = obj.cache = {}

  @functools.wraps( obj )
  def memoizer( *args, **kwargs ):
    key = str( args ) + str( kwargs )
    if key not in cache:
      cache[ key ] = obj( *args, **kwargs )
    return cache[ key ]
  return memoizer


def ForceSemanticCompletion( request_data ):
  return ( 'force_semantic' in request_data and
           bool( request_data[ 'force_semantic' ] ) )