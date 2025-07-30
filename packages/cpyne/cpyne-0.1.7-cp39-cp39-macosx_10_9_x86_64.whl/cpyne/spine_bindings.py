r"""Wrapper for manual_binding.h

Generated with:
/Library/Frameworks/Python.framework/Versions/Current/bin/ctypesgen manual_binding.h -I src/spine-c/include/spine -L src/cpyne -lspine -o src/cpyne/spine_bindings.py

Do not modify this file.
"""

__docformat__ = "restructuredtext"

# Begin preamble for Python

import ctypes
import sys
from ctypes import *  # noqa: F401, F403

_int_types = (ctypes.c_int16, ctypes.c_int32)
if hasattr(ctypes, "c_int64"):
    # Some builds of ctypes apparently do not have ctypes.c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (ctypes.c_int64,)
for t in _int_types:
    if ctypes.sizeof(t) == ctypes.sizeof(ctypes.c_size_t):
        c_ptrdiff_t = t
del t
del _int_types



class UserString:
    def __init__(self, seq):
        if isinstance(seq, bytes):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq).encode()

    def __bytes__(self):
        return self.data

    def __str__(self):
        return self.data.decode()

    def __repr__(self):
        return repr(self.data)

    def __int__(self):
        return int(self.data.decode())

    def __long__(self):
        return int(self.data.decode())

    def __float__(self):
        return float(self.data.decode())

    def __complex__(self):
        return complex(self.data.decode())

    def __hash__(self):
        return hash(self.data)

    def __le__(self, string):
        if isinstance(string, UserString):
            return self.data <= string.data
        else:
            return self.data <= string

    def __lt__(self, string):
        if isinstance(string, UserString):
            return self.data < string.data
        else:
            return self.data < string

    def __ge__(self, string):
        if isinstance(string, UserString):
            return self.data >= string.data
        else:
            return self.data >= string

    def __gt__(self, string):
        if isinstance(string, UserString):
            return self.data > string.data
        else:
            return self.data > string

    def __eq__(self, string):
        if isinstance(string, UserString):
            return self.data == string.data
        else:
            return self.data == string

    def __ne__(self, string):
        if isinstance(string, UserString):
            return self.data != string.data
        else:
            return self.data != string

    def __contains__(self, char):
        return char in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.__class__(self.data[index])

    def __getslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, bytes):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other).encode())

    def __radd__(self, other):
        if isinstance(other, bytes):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other).encode() + self.data)

    def __mul__(self, n):
        return self.__class__(self.data * n)

    __rmul__ = __mul__

    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self):
        return self.__class__(self.data.capitalize())

    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))

    def count(self, sub, start=0, end=sys.maxsize):
        return self.data.count(sub, start, end)

    def decode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())

    def encode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())

    def endswith(self, suffix, start=0, end=sys.maxsize):
        return self.data.endswith(suffix, start, end)

    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))

    def find(self, sub, start=0, end=sys.maxsize):
        return self.data.find(sub, start, end)

    def index(self, sub, start=0, end=sys.maxsize):
        return self.data.index(sub, start, end)

    def isalpha(self):
        return self.data.isalpha()

    def isalnum(self):
        return self.data.isalnum()

    def isdecimal(self):
        return self.data.isdecimal()

    def isdigit(self):
        return self.data.isdigit()

    def islower(self):
        return self.data.islower()

    def isnumeric(self):
        return self.data.isnumeric()

    def isspace(self):
        return self.data.isspace()

    def istitle(self):
        return self.data.istitle()

    def isupper(self):
        return self.data.isupper()

    def join(self, seq):
        return self.data.join(seq)

    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))

    def lower(self):
        return self.__class__(self.data.lower())

    def lstrip(self, chars=None):
        return self.__class__(self.data.lstrip(chars))

    def partition(self, sep):
        return self.data.partition(sep)

    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))

    def rfind(self, sub, start=0, end=sys.maxsize):
        return self.data.rfind(sub, start, end)

    def rindex(self, sub, start=0, end=sys.maxsize):
        return self.data.rindex(sub, start, end)

    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))

    def rpartition(self, sep):
        return self.data.rpartition(sep)

    def rstrip(self, chars=None):
        return self.__class__(self.data.rstrip(chars))

    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)

    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)

    def splitlines(self, keepends=0):
        return self.data.splitlines(keepends)

    def startswith(self, prefix, start=0, end=sys.maxsize):
        return self.data.startswith(prefix, start, end)

    def strip(self, chars=None):
        return self.__class__(self.data.strip(chars))

    def swapcase(self):
        return self.__class__(self.data.swapcase())

    def title(self):
        return self.__class__(self.data.title())

    def translate(self, *args):
        return self.__class__(self.data.translate(*args))

    def upper(self):
        return self.__class__(self.data.upper())

    def zfill(self, width):
        return self.__class__(self.data.zfill(width))


class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""

    def __init__(self, string=""):
        self.data = string

    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")

    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + sub + self.data[index + 1 :]

    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + self.data[index + 1 :]

    def __setslice__(self, start, end, sub):
        start = max(start, 0)
        end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start] + sub.data + self.data[end:]
        elif isinstance(sub, bytes):
            self.data = self.data[:start] + sub + self.data[end:]
        else:
            self.data = self.data[:start] + str(sub).encode() + self.data[end:]

    def __delslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]

    def immutable(self):
        return UserString(self.data)

    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, bytes):
            self.data += other
        else:
            self.data += str(other).encode()
        return self

    def __imul__(self, n):
        self.data *= n
        return self


class String(MutableString, ctypes.Union):

    _fields_ = [("raw", ctypes.POINTER(ctypes.c_char)), ("data", ctypes.c_char_p)]

    def __init__(self, obj=b""):
        if isinstance(obj, (bytes, UserString)):
            self.data = bytes(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(ctypes.POINTER(ctypes.c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from bytes
        elif isinstance(obj, bytes):
            return cls(obj)

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj.encode())

        # Convert from c_char_p
        elif isinstance(obj, ctypes.c_char_p):
            return obj

        # Convert from POINTER(ctypes.c_char)
        elif isinstance(obj, ctypes.POINTER(ctypes.c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(ctypes.cast(obj, ctypes.POINTER(ctypes.c_char)))

        # Convert from ctypes.c_char array
        elif isinstance(obj, ctypes.c_char * len(obj)):
            return obj

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)

    from_param = classmethod(from_param)


def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)


# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to ctypes.c_void_p.
def UNCHECKED(type):
    if hasattr(type, "_type_") and isinstance(type._type_, str) and type._type_ != "P":
        return type
    else:
        return ctypes.c_void_p


# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self, func, restype, argtypes, errcheck):
        self.func = func
        self.func.restype = restype
        self.argtypes = argtypes
        if errcheck:
            self.func.errcheck = errcheck

    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func

    def __call__(self, *args):
        fixed_args = []
        i = 0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i += 1
        return self.func(*fixed_args + list(args[i:]))


def ord_if_char(value):
    """
    Simple helper used for casts to simple builtin types:  if the argument is a
    string type, it will be converted to it's ordinal value.

    This function will raise an exception if the argument is string with more
    than one characters.
    """
    return ord(value) if (isinstance(value, bytes) or isinstance(value, str)) else value

# End preamble

_libs = {}
_libdirs = ['src/cpyne']

# Begin loader

"""
Load libraries - appropriately for all our supported platforms
"""
# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import ctypes
import ctypes.util
import glob
import os.path
import platform
import re
import sys


def _environ_path(name):
    """Split an environment variable into a path-like list elements"""
    if name in os.environ:
        return os.environ[name].split(":")
    return []


class LibraryLoader:
    """
    A base class For loading of libraries ;-)
    Subclasses load libraries for specific platforms.
    """

    # library names formatted specifically for platforms
    name_formats = ["%s"]

    class Lookup:
        """Looking up calling conventions for a platform"""

        mode = ctypes.DEFAULT_MODE

        def __init__(self, path):
            super(LibraryLoader.Lookup, self).__init__()
            self.access = dict(cdecl=ctypes.CDLL(path, self.mode))

        def get(self, name, calling_convention="cdecl"):
            """Return the given name according to the selected calling convention"""
            if calling_convention not in self.access:
                raise LookupError(
                    "Unknown calling convention '{}' for function '{}'".format(
                        calling_convention, name
                    )
                )
            return getattr(self.access[calling_convention], name)

        def has(self, name, calling_convention="cdecl"):
            """Return True if this given calling convention finds the given 'name'"""
            if calling_convention not in self.access:
                return False
            return hasattr(self.access[calling_convention], name)

        def __getattr__(self, name):
            return getattr(self.access["cdecl"], name)

    def __init__(self):
        self.other_dirs = []

    def __call__(self, libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            # noinspection PyBroadException
            try:
                return self.Lookup(path)
            except Exception:  # pylint: disable=broad-except
                pass

        raise ImportError("Could not load %s." % libname)

    def getpaths(self, libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname
        else:
            # search through a prioritized series of locations for the library

            # we first search any specific directories identified by user
            for dir_i in self.other_dirs:
                for fmt in self.name_formats:
                    # dir_i should be absolute already
                    yield os.path.join(dir_i, fmt % libname)

            # check if this code is even stored in a physical file
            try:
                this_file = __file__
            except NameError:
                this_file = None

            # then we search the directory where the generated python interface is stored
            if this_file is not None:
                for fmt in self.name_formats:
                    yield os.path.abspath(os.path.join(os.path.dirname(__file__), fmt % libname))

            # now, use the ctypes tools to try to find the library
            for fmt in self.name_formats:
                path = ctypes.util.find_library(fmt % libname)
                if path:
                    yield path

            # then we search all paths identified as platform-specific lib paths
            for path in self.getplatformpaths(libname):
                yield path

            # Finally, we'll try the users current working directory
            for fmt in self.name_formats:
                yield os.path.abspath(os.path.join(os.path.curdir, fmt % libname))

    def getplatformpaths(self, _libname):  # pylint: disable=no-self-use
        """Return all the library paths available in this platform"""
        return []


# Darwin (Mac OS X)


class DarwinLibraryLoader(LibraryLoader):
    """Library loader for MacOS"""

    name_formats = [
        "lib%s.dylib",
        "lib%s.so",
        "lib%s.bundle",
        "%s.dylib",
        "%s.so",
        "%s.bundle",
        "%s",
    ]

    class Lookup(LibraryLoader.Lookup):
        """
        Looking up library files for this platform (Darwin aka MacOS)
        """

        # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
        # of the default RTLD_LOCAL.  Without this, you end up with
        # libraries not being loadable, resulting in "Symbol not found"
        # errors
        mode = ctypes.RTLD_GLOBAL

    def getplatformpaths(self, libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [fmt % libname for fmt in self.name_formats]

        for directory in self.getdirs(libname):
            for name in names:
                yield os.path.join(directory, name)

    @staticmethod
    def getdirs(libname):
        """Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        """

        dyld_fallback_library_path = _environ_path("DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [
                os.path.expanduser("~/lib"),
                "/usr/local/lib",
                "/usr/lib",
            ]

        dirs = []

        if "/" in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
            dirs.extend(_environ_path("LD_RUN_PATH"))

        if hasattr(sys, "frozen") and getattr(sys, "frozen") == "macosx_app":
            dirs.append(os.path.join(os.environ["RESOURCEPATH"], "..", "Frameworks"))

        dirs.extend(dyld_fallback_library_path)

        return dirs


# Posix


class PosixLibraryLoader(LibraryLoader):
    """Library loader for POSIX-like systems (including Linux)"""

    _ld_so_cache = None

    _include = re.compile(r"^\s*include\s+(?P<pattern>.*)")

    name_formats = ["lib%s.so", "%s.so", "%s"]

    class _Directories(dict):
        """Deal with directories"""

        def __init__(self):
            dict.__init__(self)
            self.order = 0

        def add(self, directory):
            """Add a directory to our current set of directories"""
            if len(directory) > 1:
                directory = directory.rstrip(os.path.sep)
            # only adds and updates order if exists and not already in set
            if not os.path.exists(directory):
                return
            order = self.setdefault(directory, self.order)
            if order == self.order:
                self.order += 1

        def extend(self, directories):
            """Add a list of directories to our set"""
            for a_dir in directories:
                self.add(a_dir)

        def ordered(self):
            """Sort the list of directories"""
            return (i[0] for i in sorted(self.items(), key=lambda d: d[1]))

    def _get_ld_so_conf_dirs(self, conf, dirs):
        """
        Recursive function to help parse all ld.so.conf files, including proper
        handling of the `include` directive.
        """

        try:
            with open(conf) as fileobj:
                for dirname in fileobj:
                    dirname = dirname.strip()
                    if not dirname:
                        continue

                    match = self._include.match(dirname)
                    if not match:
                        dirs.add(dirname)
                    else:
                        for dir2 in glob.glob(match.group("pattern")):
                            self._get_ld_so_conf_dirs(dir2, dirs)
        except IOError:
            pass

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        #
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = self._Directories()
        for name in (
            "LD_LIBRARY_PATH",
            "SHLIB_PATH",  # HP-UX
            "LIBPATH",  # OS/2, AIX
            "LIBRARY_PATH",  # BE/OS
        ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))

        self._get_ld_so_conf_dirs("/etc/ld.so.conf", directories)

        bitage = platform.architecture()[0]

        unix_lib_dirs_list = []
        if bitage.startswith("64"):
            # prefer 64 bit if that is our arch
            unix_lib_dirs_list += ["/lib64", "/usr/lib64"]

        # must include standard libs, since those paths are also used by 64 bit
        # installs
        unix_lib_dirs_list += ["/lib", "/usr/lib"]
        if sys.platform.startswith("linux"):
            # Try and support multiarch work in Ubuntu
            # https://wiki.ubuntu.com/MultiarchSpec
            if bitage.startswith("32"):
                # Assume Intel/AMD x86 compat
                unix_lib_dirs_list += ["/lib/i386-linux-gnu", "/usr/lib/i386-linux-gnu"]
            elif bitage.startswith("64"):
                # Assume Intel/AMD x86 compatible
                unix_lib_dirs_list += [
                    "/lib/x86_64-linux-gnu",
                    "/usr/lib/x86_64-linux-gnu",
                ]
            else:
                # guess...
                unix_lib_dirs_list += glob.glob("/lib/*linux-gnu")
        directories.extend(unix_lib_dirs_list)

        cache = {}
        lib_re = re.compile(r"lib(.*)\.s[ol]")
        # ext_re = re.compile(r"\.s[ol]$")
        for our_dir in directories.ordered():
            try:
                for path in glob.glob("%s/*.s[ol]*" % our_dir):
                    file = os.path.basename(path)

                    # Index by filename
                    cache_i = cache.setdefault(file, set())
                    cache_i.add(path)

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        cache_i = cache.setdefault(library, set())
                        cache_i.add(path)
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname, set())
        for i in result:
            # we iterate through all found paths for library, since we may have
            # actually found multiple architectures or other library types that
            # may not load
            yield i


# Windows


class WindowsLibraryLoader(LibraryLoader):
    """Library loader for Microsoft Windows"""

    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll", "%s"]

    class Lookup(LibraryLoader.Lookup):
        """Lookup class for Windows libraries..."""

        def __init__(self, path):
            super(WindowsLibraryLoader.Lookup, self).__init__(path)
            self.access["stdcall"] = ctypes.windll.LoadLibrary(path)


# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin": DarwinLibraryLoader,
    "cygwin": WindowsLibraryLoader,
    "win32": WindowsLibraryLoader,
    "msys": WindowsLibraryLoader,
}

load_library = loaderclass.get(sys.platform, PosixLibraryLoader)()


def add_library_search_dirs(other_dirs):
    """
    Add libraries to search paths.
    If library paths are relative, convert them to absolute with respect to this
    file's directory
    """
    for path in other_dirs:
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        load_library.other_dirs.append(path)


del loaderclass

# End loader

add_library_search_dirs(['src/cpyne'])

# Begin libraries
_libs["spine"] = load_library("spine")

# 1 libraries
# End libraries

# No modules

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 5
class struct_spVertexAttachment(Structure):
    pass

spVertexAttachment = struct_spVertexAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 5

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 6
class struct_spAtlasPage(Structure):
    pass

spAtlasPage = struct_spAtlasPage# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 6

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 7
class struct_spAtlasRegion(Structure):
    pass

spAtlasRegion = struct_spAtlasRegion# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 7

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 8
class struct_spMeshAttachment(Structure):
    pass

spMeshAttachment = struct_spMeshAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 8

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 10
class struct_spAtlas(Structure):
    pass

spAtlas = struct_spAtlas# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 10

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 11
class struct_spAnimationState(Structure):
    pass

spAnimationState = struct_spAnimationState# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 11

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 12
class struct_spFloatArray(Structure):
    pass

spFloatArray = struct_spFloatArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 12

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 15
class struct_spSkeleton(Structure):
    pass

spSkeleton = struct_spSkeleton# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 15

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 16
class struct_spSkeletonData(Structure):
    pass

spSkeletonData = struct_spSkeletonData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 16

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 17
class struct_spSkin(Structure):
    pass

spSkin = struct_spSkin# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 17

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 18
class struct_spSlot(Structure):
    pass

spSlot = struct_spSlot# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 18

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 19
class struct_spSlotData(Structure):
    pass

spSlotData = struct_spSlotData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 19

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 20
class struct_spBone(Structure):
    pass

spBone = struct_spBone# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 20

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 21
class struct_spBoneData(Structure):
    pass

spBoneData = struct_spBoneData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 21

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 22
class struct_spAttachment(Structure):
    pass

spAttachment = struct_spAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 22

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 23
class struct_spAttachmentLoader(Structure):
    pass

spAttachmentLoader = struct_spAttachmentLoader# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 23

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 24
class struct_spAttachmentTimeline(Structure):
    pass

spAttachmentTimeline = struct_spAttachmentTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 24

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 25
class struct_spEvent(Structure):
    pass

spEvent = struct_spEvent# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 25

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 26
class struct_spEventData(Structure):
    pass

spEventData = struct_spEventData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 26

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 27
class struct_spTimeline(Structure):
    pass

spTimeline = struct_spTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 27

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 28
class struct_spCurveTimeline(Structure):
    pass

spCurveTimeline = struct_spCurveTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 28

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 29
class struct_spVertexEffect(Structure):
    pass

spVertexEffect = struct_spVertexEffect# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 29

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 30
class struct_spJitterVertexEffect(Structure):
    pass

spJitterVertexEffect = struct_spJitterVertexEffect# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 30

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 31
class struct_spSwirlVertexEffect(Structure):
    pass

spSwirlVertexEffect = struct_spSwirlVertexEffect# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 31

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 32
class struct_spTransformConstraint(Structure):
    pass

spTransformConstraint = struct_spTransformConstraint# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 32

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 33
class struct_spTransformConstraintData(Structure):
    pass

spTransformConstraintData = struct_spTransformConstraintData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 33

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 34
class struct_spIkConstraint(Structure):
    pass

spIkConstraint = struct_spIkConstraint# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 34

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 35
class struct_spIkConstraintData(Structure):
    pass

spIkConstraintData = struct_spIkConstraintData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 35

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 36
class struct_spPathConstraint(Structure):
    pass

spPathConstraint = struct_spPathConstraint# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 36

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 37
class struct_spPathConstraintData(Structure):
    pass

spPathConstraintData = struct_spPathConstraintData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 37

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 38
class struct_spRegionAttachment(Structure):
    pass

spRegionAttachment = struct_spRegionAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 38

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 39
class struct_spClippingAttachment(Structure):
    pass

spClippingAttachment = struct_spClippingAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 39

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 40
class struct_spPointAttachment(Structure):
    pass

spPointAttachment = struct_spPointAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 40

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 41
class struct_spPathAttachment(Structure):
    pass

spPathAttachment = struct_spPathAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 41

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 42
class struct_spColor(Structure):
    pass

spColor = struct_spColor# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 42

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 43
class struct_spSkeletonJson(Structure):
    pass

spSkeletonJson = struct_spSkeletonJson# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 43

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 44
class struct_spSkeletonBinary(Structure):
    pass

spSkeletonBinary = struct_spSkeletonBinary# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 44

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 45
class struct_spAnimation(Structure):
    pass

spAnimation = struct_spAnimation# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 45

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 46
class struct_spAnimationStateData(Structure):
    pass

spAnimationStateData = struct_spAnimationStateData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 46

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 47
class struct_spTriangulator(Structure):
    pass

spTriangulator = struct_spTriangulator# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 47

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 48
class struct_spArrayFloatArray(Structure):
    pass

spArrayFloatArray = struct_spArrayFloatArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 48

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 49
class struct_spArrayShortArray(Structure):
    pass

spArrayShortArray = struct_spArrayShortArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 49

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 50
class struct_spShortArray(Structure):
    pass

spShortArray = struct_spShortArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 50

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 51
class struct_spIntArray(Structure):
    pass

spIntArray = struct_spIntArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 51

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 52
class struct_spUnsignedShortArray(Structure):
    pass

spUnsignedShortArray = struct_spUnsignedShortArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 52

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 53
class struct_spBoneDataArray(Structure):
    pass

spBoneDataArray = struct_spBoneDataArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 53

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 54
class struct_spIkConstraintDataArray(Structure):
    pass

spIkConstraintDataArray = struct_spIkConstraintDataArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 54

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 55
class struct_spTransformConstraintDataArray(Structure):
    pass

spTransformConstraintDataArray = struct_spTransformConstraintDataArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 55

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 56
class struct_spPathConstraintDataArray(Structure):
    pass

spPathConstraintDataArray = struct_spPathConstraintDataArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 56

CreateTextureCallback = CFUNCTYPE(UNCHECKED(None), POINTER(spAtlasPage), String)# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 60

DisposeTextureCallback = CFUNCTYPE(UNCHECKED(None), POINTER(spAtlasPage))# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 61

spAnimationStateListener = CFUNCTYPE(UNCHECKED(None), POINTER(struct_spAnimationState), c_int, c_int, POINTER(struct_spEvent), c_int)# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 62

spTimelineApplyFunc = CFUNCTYPE(UNCHECKED(None), POINTER(None), c_float, c_float, POINTER(c_float), c_float, c_float, c_int, c_int, POINTER(None))# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 63

spVertexEffectBeginFunc = CFUNCTYPE(UNCHECKED(None), POINTER(None))# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 66

spVertexEffectTransformFunc = CFUNCTYPE(UNCHECKED(None), POINTER(None), POINTER(c_float), c_int)# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 67

spVertexEffectEndFunc = CFUNCTYPE(UNCHECKED(None), POINTER(None))# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 68

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 89
class struct_spBaseTimeline(Structure):
    pass

struct_spBaseTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'boneIndex',
]
struct_spBaseTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('boneIndex', c_int),
]

spBaseTimeline = struct_spBaseTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 89

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 96
class struct_spColorTimeline(Structure):
    pass

struct_spColorTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'slotIndex',
]
struct_spColorTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('slotIndex', c_int),
]

spColorTimeline = struct_spColorTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 96

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 103
class struct_spTwoColorTimeline(Structure):
    pass

struct_spTwoColorTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'slotIndex',
]
struct_spTwoColorTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('slotIndex', c_int),
]

spTwoColorTimeline = struct_spTwoColorTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 103

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 118
class struct_spEventTimeline(Structure):
    pass

struct_spEventTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'events',
]
struct_spEventTimeline._fields_ = [
    ('super', struct_spTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('events', POINTER(POINTER(struct_spEvent))),
]

spEventTimeline = struct_spEventTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 118

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 126
class struct_spDrawOrderTimeline(Structure):
    pass

struct_spDrawOrderTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'drawOrders',
    'slotsCount',
]
struct_spDrawOrderTimeline._fields_ = [
    ('super', struct_spTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('drawOrders', POINTER(POINTER(c_int))),
    ('slotsCount', c_int),
]

spDrawOrderTimeline = struct_spDrawOrderTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 126

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 136
class struct_spDeformTimeline(Structure):
    pass

struct_spDeformTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'frameVerticesCount',
    'frameVertices',
    'slotIndex',
    'attachment',
]
struct_spDeformTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('frameVerticesCount', c_int),
    ('frameVertices', POINTER(POINTER(c_float))),
    ('slotIndex', c_int),
    ('attachment', POINTER(struct_spAttachment)),
]

spDeformTimeline = struct_spDeformTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 136

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 143
class struct_spIkConstraintTimeline(Structure):
    pass

struct_spIkConstraintTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'ikConstraintIndex',
]
struct_spIkConstraintTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('ikConstraintIndex', c_int),
]

spIkConstraintTimeline = struct_spIkConstraintTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 143

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 150
class struct_spTransformConstraintTimeline(Structure):
    pass

struct_spTransformConstraintTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'transformConstraintIndex',
]
struct_spTransformConstraintTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('transformConstraintIndex', c_int),
]

spTransformConstraintTimeline = struct_spTransformConstraintTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 150

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 157
class struct_spPathConstraintPositionTimeline(Structure):
    pass

struct_spPathConstraintPositionTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'pathConstraintIndex',
]
struct_spPathConstraintPositionTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('pathConstraintIndex', c_int),
]

spPathConstraintPositionTimeline = struct_spPathConstraintPositionTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 157

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 164
class struct_spPathConstraintSpacingTimeline(Structure):
    pass

struct_spPathConstraintSpacingTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'pathConstraintIndex',
]
struct_spPathConstraintSpacingTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('pathConstraintIndex', c_int),
]

spPathConstraintSpacingTimeline = struct_spPathConstraintSpacingTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 164

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 171
class struct_spPathConstraintMixTimeline(Structure):
    pass

struct_spPathConstraintMixTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'pathConstraintIndex',
]
struct_spPathConstraintMixTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('pathConstraintIndex', c_int),
]

spPathConstraintMixTimeline = struct_spPathConstraintMixTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 171

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 203
class struct_spSkeletonClipping(Structure):
    pass

struct_spSkeletonClipping.__slots__ = [
    'triangulator',
    'clippingPolygon',
    'clipOutput',
    'clippedVertices',
    'clippedUVs',
    'clippedTriangles',
    'scratch',
    'clipAttachment',
    'clippingPolygons',
]
struct_spSkeletonClipping._fields_ = [
    ('triangulator', POINTER(struct_spTriangulator)),
    ('clippingPolygon', POINTER(struct_spFloatArray)),
    ('clipOutput', POINTER(struct_spFloatArray)),
    ('clippedVertices', POINTER(struct_spFloatArray)),
    ('clippedUVs', POINTER(struct_spFloatArray)),
    ('clippedTriangles', POINTER(struct_spUnsignedShortArray)),
    ('scratch', POINTER(struct_spFloatArray)),
    ('clipAttachment', POINTER(struct_spClippingAttachment)),
    ('clippingPolygons', POINTER(struct_spArrayFloatArray)),
]

spSkeletonClipping = struct_spSkeletonClipping# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 203

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 512
if _libs["spine"].has("spAtlas_createFromFile", "cdecl"):
    spAtlas_createFromFile = _libs["spine"].get("spAtlas_createFromFile", "cdecl")
    spAtlas_createFromFile.argtypes = [String, POINTER(None)]
    spAtlas_createFromFile.restype = POINTER(spAtlas)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 513
if _libs["spine"].has("spAtlas_dispose", "cdecl"):
    spAtlas_dispose = _libs["spine"].get("spAtlas_dispose", "cdecl")
    spAtlas_dispose.argtypes = [POINTER(spAtlas)]
    spAtlas_dispose.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 516
if _libs["spine"].has("spAtlasPage_set_createTexture", "cdecl"):
    spAtlasPage_set_createTexture = _libs["spine"].get("spAtlasPage_set_createTexture", "cdecl")
    spAtlasPage_set_createTexture.argtypes = [CreateTextureCallback]
    spAtlasPage_set_createTexture.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 517
if _libs["spine"].has("spAtlasPage_set_disposeTexture", "cdecl"):
    spAtlasPage_set_disposeTexture = _libs["spine"].get("spAtlasPage_set_disposeTexture", "cdecl")
    spAtlasPage_set_disposeTexture.argtypes = [DisposeTextureCallback]
    spAtlasPage_set_disposeTexture.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 520
if _libs["spine"].has("spSkeletonJson_create", "cdecl"):
    spSkeletonJson_create = _libs["spine"].get("spSkeletonJson_create", "cdecl")
    spSkeletonJson_create.argtypes = [POINTER(spAtlas)]
    spSkeletonJson_create.restype = POINTER(spSkeletonJson)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 521
if _libs["spine"].has("spSkeletonJson_dispose", "cdecl"):
    spSkeletonJson_dispose = _libs["spine"].get("spSkeletonJson_dispose", "cdecl")
    spSkeletonJson_dispose.argtypes = [POINTER(spSkeletonJson)]
    spSkeletonJson_dispose.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 522
if _libs["spine"].has("spSkeletonJson_readSkeletonDataFile", "cdecl"):
    spSkeletonJson_readSkeletonDataFile = _libs["spine"].get("spSkeletonJson_readSkeletonDataFile", "cdecl")
    spSkeletonJson_readSkeletonDataFile.argtypes = [POINTER(spSkeletonJson), String]
    spSkeletonJson_readSkeletonDataFile.restype = POINTER(spSkeletonData)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 525
if _libs["spine"].has("spSkeletonBinary_create", "cdecl"):
    spSkeletonBinary_create = _libs["spine"].get("spSkeletonBinary_create", "cdecl")
    spSkeletonBinary_create.argtypes = [POINTER(spAtlas)]
    spSkeletonBinary_create.restype = POINTER(spSkeletonBinary)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 526
if _libs["spine"].has("spSkeletonBinary_dispose", "cdecl"):
    spSkeletonBinary_dispose = _libs["spine"].get("spSkeletonBinary_dispose", "cdecl")
    spSkeletonBinary_dispose.argtypes = [POINTER(spSkeletonBinary)]
    spSkeletonBinary_dispose.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 527
if _libs["spine"].has("spSkeletonBinary_readSkeletonDataFile", "cdecl"):
    spSkeletonBinary_readSkeletonDataFile = _libs["spine"].get("spSkeletonBinary_readSkeletonDataFile", "cdecl")
    spSkeletonBinary_readSkeletonDataFile.argtypes = [POINTER(spSkeletonBinary), String]
    spSkeletonBinary_readSkeletonDataFile.restype = POINTER(spSkeletonData)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 530
if _libs["spine"].has("spSkeleton_create", "cdecl"):
    spSkeleton_create = _libs["spine"].get("spSkeleton_create", "cdecl")
    spSkeleton_create.argtypes = [POINTER(spSkeletonData)]
    spSkeleton_create.restype = POINTER(spSkeleton)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 531
if _libs["spine"].has("spSkeleton_dispose", "cdecl"):
    spSkeleton_dispose = _libs["spine"].get("spSkeleton_dispose", "cdecl")
    spSkeleton_dispose.argtypes = [POINTER(spSkeleton)]
    spSkeleton_dispose.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 532
if _libs["spine"].has("spSkeleton_update", "cdecl"):
    spSkeleton_update = _libs["spine"].get("spSkeleton_update", "cdecl")
    spSkeleton_update.argtypes = [POINTER(spSkeleton), c_float]
    spSkeleton_update.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 533
if _libs["spine"].has("spSkeleton_setSkinByName", "cdecl"):
    spSkeleton_setSkinByName = _libs["spine"].get("spSkeleton_setSkinByName", "cdecl")
    spSkeleton_setSkinByName.argtypes = [POINTER(spSkeleton), String]
    spSkeleton_setSkinByName.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 534
if _libs["spine"].has("spSkeleton_setToSetupPose", "cdecl"):
    spSkeleton_setToSetupPose = _libs["spine"].get("spSkeleton_setToSetupPose", "cdecl")
    spSkeleton_setToSetupPose.argtypes = [POINTER(spSkeleton)]
    spSkeleton_setToSetupPose.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 535
if _libs["spine"].has("spSkeleton_updateWorldTransform", "cdecl"):
    spSkeleton_updateWorldTransform = _libs["spine"].get("spSkeleton_updateWorldTransform", "cdecl")
    spSkeleton_updateWorldTransform.argtypes = [POINTER(spSkeleton)]
    spSkeleton_updateWorldTransform.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 537
if _libs["spine"].has("spSkeleton_findBone", "cdecl"):
    spSkeleton_findBone = _libs["spine"].get("spSkeleton_findBone", "cdecl")
    spSkeleton_findBone.argtypes = [POINTER(spSkeleton), String]
    spSkeleton_findBone.restype = POINTER(spBone)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 538
if _libs["spine"].has("spSkeleton_findSlot", "cdecl"):
    spSkeleton_findSlot = _libs["spine"].get("spSkeleton_findSlot", "cdecl")
    spSkeleton_findSlot.argtypes = [POINTER(spSkeleton), String]
    spSkeleton_findSlot.restype = POINTER(spSlot)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 539
if _libs["spine"].has("spSkeleton_getAttachmentForSlotName", "cdecl"):
    spSkeleton_getAttachmentForSlotName = _libs["spine"].get("spSkeleton_getAttachmentForSlotName", "cdecl")
    spSkeleton_getAttachmentForSlotName.argtypes = [POINTER(spSkeleton), String, String]
    spSkeleton_getAttachmentForSlotName.restype = POINTER(spAttachment)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 542
if _libs["spine"].has("spAnimationStateData_create", "cdecl"):
    spAnimationStateData_create = _libs["spine"].get("spAnimationStateData_create", "cdecl")
    spAnimationStateData_create.argtypes = [POINTER(spSkeletonData)]
    spAnimationStateData_create.restype = POINTER(spAnimationStateData)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 543
if _libs["spine"].has("spAnimationStateData_dispose", "cdecl"):
    spAnimationStateData_dispose = _libs["spine"].get("spAnimationStateData_dispose", "cdecl")
    spAnimationStateData_dispose.argtypes = [POINTER(spAnimationStateData)]
    spAnimationStateData_dispose.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 545
if _libs["spine"].has("spAnimationState_create", "cdecl"):
    spAnimationState_create = _libs["spine"].get("spAnimationState_create", "cdecl")
    spAnimationState_create.argtypes = [POINTER(spAnimationStateData)]
    spAnimationState_create.restype = POINTER(spAnimationState)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 546
if _libs["spine"].has("spAnimationState_dispose", "cdecl"):
    spAnimationState_dispose = _libs["spine"].get("spAnimationState_dispose", "cdecl")
    spAnimationState_dispose.argtypes = [POINTER(spAnimationState)]
    spAnimationState_dispose.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 547
if _libs["spine"].has("spAnimationState_update", "cdecl"):
    spAnimationState_update = _libs["spine"].get("spAnimationState_update", "cdecl")
    spAnimationState_update.argtypes = [POINTER(spAnimationState), c_float]
    spAnimationState_update.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 548
if _libs["spine"].has("spAnimationState_apply", "cdecl"):
    spAnimationState_apply = _libs["spine"].get("spAnimationState_apply", "cdecl")
    spAnimationState_apply.argtypes = [POINTER(spAnimationState), POINTER(spSkeleton)]
    spAnimationState_apply.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 549
if _libs["spine"].has("spAnimationState_setAnimationByName", "cdecl"):
    spAnimationState_setAnimationByName = _libs["spine"].get("spAnimationState_setAnimationByName", "cdecl")
    spAnimationState_setAnimationByName.argtypes = [POINTER(spAnimationState), c_int, String, c_int]
    spAnimationState_setAnimationByName.restype = c_int

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 550
if _libs["spine"].has("spAnimationState_addAnimationByName", "cdecl"):
    spAnimationState_addAnimationByName = _libs["spine"].get("spAnimationState_addAnimationByName", "cdecl")
    spAnimationState_addAnimationByName.argtypes = [POINTER(spAnimationState), c_int, String, c_int, c_float]
    spAnimationState_addAnimationByName.restype = c_int

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 552
for _lib in _libs.values():
    if not _lib.has("spAnimationState_setListener", "cdecl"):
        continue
    spAnimationState_setListener = _lib.get("spAnimationState_setListener", "cdecl")
    spAnimationState_setListener.argtypes = [POINTER(spAnimationState), spAnimationStateListener]
    spAnimationState_setListener.restype = None
    break

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 553
for _lib in _libs.values():
    if not _lib.has("spAnimationState_setVertexEffect", "cdecl"):
        continue
    spAnimationState_setVertexEffect = _lib.get("spAnimationState_setVertexEffect", "cdecl")
    spAnimationState_setVertexEffect.argtypes = [POINTER(spAnimationState), POINTER(spVertexEffect)]
    spAnimationState_setVertexEffect.restype = None
    break

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 556
if _libs["spine"].has("spSkeletonData_findAnimation", "cdecl"):
    spSkeletonData_findAnimation = _libs["spine"].get("spSkeletonData_findAnimation", "cdecl")
    spSkeletonData_findAnimation.argtypes = [POINTER(spSkeletonData), String]
    spSkeletonData_findAnimation.restype = POINTER(spAnimation)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 559
if _libs["spine"].has("spSkeletonData_findSkin", "cdecl"):
    spSkeletonData_findSkin = _libs["spine"].get("spSkeletonData_findSkin", "cdecl")
    spSkeletonData_findSkin.argtypes = [POINTER(spSkeletonData), String]
    spSkeletonData_findSkin.restype = POINTER(spSkin)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 560
if _libs["spine"].has("spSkeleton_setSkin", "cdecl"):
    spSkeleton_setSkin = _libs["spine"].get("spSkeleton_setSkin", "cdecl")
    spSkeleton_setSkin.argtypes = [POINTER(spSkeleton), POINTER(spSkin)]
    spSkeleton_setSkin.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 563
if _libs["spine"].has("spSkeleton_findIkConstraint", "cdecl"):
    spSkeleton_findIkConstraint = _libs["spine"].get("spSkeleton_findIkConstraint", "cdecl")
    spSkeleton_findIkConstraint.argtypes = [POINTER(spSkeleton), String]
    spSkeleton_findIkConstraint.restype = POINTER(spIkConstraint)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 564
if _libs["spine"].has("spSkeleton_findTransformConstraint", "cdecl"):
    spSkeleton_findTransformConstraint = _libs["spine"].get("spSkeleton_findTransformConstraint", "cdecl")
    spSkeleton_findTransformConstraint.argtypes = [POINTER(spSkeleton), String]
    spSkeleton_findTransformConstraint.restype = POINTER(spTransformConstraint)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 565
if _libs["spine"].has("spSkeleton_findPathConstraint", "cdecl"):
    spSkeleton_findPathConstraint = _libs["spine"].get("spSkeleton_findPathConstraint", "cdecl")
    spSkeleton_findPathConstraint.argtypes = [POINTER(spSkeleton), String]
    spSkeleton_findPathConstraint.restype = POINTER(spPathConstraint)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 568
if _libs["spine"].has("spSkeleton_getAttachmentForSlotIndex", "cdecl"):
    spSkeleton_getAttachmentForSlotIndex = _libs["spine"].get("spSkeleton_getAttachmentForSlotIndex", "cdecl")
    spSkeleton_getAttachmentForSlotIndex.argtypes = [POINTER(spSkeleton), c_int, String]
    spSkeleton_getAttachmentForSlotIndex.restype = POINTER(spAttachment)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 569
if _libs["spine"].has("spRegionAttachment_create", "cdecl"):
    spRegionAttachment_create = _libs["spine"].get("spRegionAttachment_create", "cdecl")
    spRegionAttachment_create.argtypes = [String]
    spRegionAttachment_create.restype = POINTER(spRegionAttachment)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 570
if _libs["spine"].has("spMeshAttachment_create", "cdecl"):
    spMeshAttachment_create = _libs["spine"].get("spMeshAttachment_create", "cdecl")
    spMeshAttachment_create.argtypes = [String]
    spMeshAttachment_create.restype = POINTER(spMeshAttachment)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 573
if _libs["spine"].has("spClippingAttachment_create", "cdecl"):
    spClippingAttachment_create = _libs["spine"].get("spClippingAttachment_create", "cdecl")
    spClippingAttachment_create.argtypes = [String]
    spClippingAttachment_create.restype = POINTER(spClippingAttachment)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 574
if _libs["spine"].has("spJitterVertexEffect_create", "cdecl"):
    spJitterVertexEffect_create = _libs["spine"].get("spJitterVertexEffect_create", "cdecl")
    spJitterVertexEffect_create.argtypes = [c_float, c_float]
    spJitterVertexEffect_create.restype = POINTER(spVertexEffect)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 575
for _lib in _libs.values():
    if not _lib.has("spVertexEffect_dispose", "cdecl"):
        continue
    spVertexEffect_dispose = _lib.get("spVertexEffect_dispose", "cdecl")
    spVertexEffect_dispose.argtypes = [POINTER(spVertexEffect)]
    spVertexEffect_dispose.restype = None
    break

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 578
if _libs["spine"].has("spEventData_create", "cdecl"):
    spEventData_create = _libs["spine"].get("spEventData_create", "cdecl")
    spEventData_create.argtypes = [String]
    spEventData_create.restype = POINTER(spEventData)

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 579
if _libs["spine"].has("spEventData_dispose", "cdecl"):
    spEventData_dispose = _libs["spine"].get("spEventData_dispose", "cdecl")
    spEventData_dispose.argtypes = [POINTER(spEventData)]
    spEventData_dispose.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 582
if _libs["spine"].has("spSkeleton_setBonesToSetupPose", "cdecl"):
    spSkeleton_setBonesToSetupPose = _libs["spine"].get("spSkeleton_setBonesToSetupPose", "cdecl")
    spSkeleton_setBonesToSetupPose.argtypes = [POINTER(spSkeleton)]
    spSkeleton_setBonesToSetupPose.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 583
if _libs["spine"].has("spSkeleton_setSlotsToSetupPose", "cdecl"):
    spSkeleton_setSlotsToSetupPose = _libs["spine"].get("spSkeleton_setSlotsToSetupPose", "cdecl")
    spSkeleton_setSlotsToSetupPose.argtypes = [POINTER(spSkeleton)]
    spSkeleton_setSlotsToSetupPose.restype = None

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 584
if _libs["spine"].has("spSkeleton_setAttachment", "cdecl"):
    spSkeleton_setAttachment = _libs["spine"].get("spSkeleton_setAttachment", "cdecl")
    spSkeleton_setAttachment.argtypes = [POINTER(spSkeleton), String, String]
    spSkeleton_setAttachment.restype = None

spVertexAttachment = struct_spVertexAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 5

spAtlasPage = struct_spAtlasPage# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 6

spAtlasRegion = struct_spAtlasRegion# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 7

spMeshAttachment = struct_spMeshAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 8

spAtlas = struct_spAtlas# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 10

spAnimationState = struct_spAnimationState# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 11

spFloatArray = struct_spFloatArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 12

spSkeleton = struct_spSkeleton# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 15

spSkeletonData = struct_spSkeletonData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 16

spSkin = struct_spSkin# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 17

spSlot = struct_spSlot# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 18

spSlotData = struct_spSlotData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 19

spBone = struct_spBone# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 20

spBoneData = struct_spBoneData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 21

spAttachment = struct_spAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 22

spAttachmentLoader = struct_spAttachmentLoader# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 23

spAttachmentTimeline = struct_spAttachmentTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 24

spEvent = struct_spEvent# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 25

spEventData = struct_spEventData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 26

spTimeline = struct_spTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 27

spCurveTimeline = struct_spCurveTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 28

spVertexEffect = struct_spVertexEffect# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 29

spJitterVertexEffect = struct_spJitterVertexEffect# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 30

spSwirlVertexEffect = struct_spSwirlVertexEffect# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 31

spTransformConstraint = struct_spTransformConstraint# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 32

spTransformConstraintData = struct_spTransformConstraintData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 33

spIkConstraint = struct_spIkConstraint# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 34

spIkConstraintData = struct_spIkConstraintData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 35

spPathConstraint = struct_spPathConstraint# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 36

spPathConstraintData = struct_spPathConstraintData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 37

spRegionAttachment = struct_spRegionAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 38

spClippingAttachment = struct_spClippingAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 39

spPointAttachment = struct_spPointAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 40

spPathAttachment = struct_spPathAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 41

spColor = struct_spColor# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 42

spSkeletonJson = struct_spSkeletonJson# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 43

spSkeletonBinary = struct_spSkeletonBinary# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 44

spAnimation = struct_spAnimation# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 45

spAnimationStateData = struct_spAnimationStateData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 46

spTriangulator = struct_spTriangulator# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 47

spArrayFloatArray = struct_spArrayFloatArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 48

spArrayShortArray = struct_spArrayShortArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 49

spShortArray = struct_spShortArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 50

spIntArray = struct_spIntArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 51

spUnsignedShortArray = struct_spUnsignedShortArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 52

spBoneDataArray = struct_spBoneDataArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 53

spIkConstraintDataArray = struct_spIkConstraintDataArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 54

spTransformConstraintDataArray = struct_spTransformConstraintDataArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 55

spPathConstraintDataArray = struct_spPathConstraintDataArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 56

spBaseTimeline = struct_spBaseTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 89

spColorTimeline = struct_spColorTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 96

spTwoColorTimeline = struct_spTwoColorTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 103

spEventTimeline = struct_spEventTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 118

spDrawOrderTimeline = struct_spDrawOrderTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 126

spDeformTimeline = struct_spDeformTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 136

spIkConstraintTimeline = struct_spIkConstraintTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 143

spTransformConstraintTimeline = struct_spTransformConstraintTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 150

spPathConstraintPositionTimeline = struct_spPathConstraintPositionTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 157

spPathConstraintSpacingTimeline = struct_spPathConstraintSpacingTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 164

spPathConstraintMixTimeline = struct_spPathConstraintMixTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 171

spSkeletonClipping = struct_spSkeletonClipping# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 203

# No inserted files

# No prefix-stripping

