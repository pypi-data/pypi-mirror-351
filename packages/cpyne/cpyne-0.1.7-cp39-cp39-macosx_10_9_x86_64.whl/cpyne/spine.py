r"""Wrapper for manual_binding.h

Generated with:
/Library/Frameworks/Python.framework/Versions/Current/bin/ctypesgen manual_binding.h -I src/spine-c/include -L src/cpyne -lspine -D__APPLE__ -D__MACH__ -o src/cpyne/spine_bindings.py

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

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 435
class struct_spTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 10
class struct_spAnimation(Structure):
    pass

struct_spAnimation.__slots__ = [
    'name',
    'duration',
    'timelinesCount',
    'timelines',
]
struct_spAnimation._fields_ = [
    ('name', String),
    ('duration', c_float),
    ('timelinesCount', c_int),
    ('timelines', POINTER(POINTER(struct_spTimeline))),
]

spAnimation = struct_spAnimation# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 10

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 15
class struct_spCurveTimeline(Structure):
    pass

struct_spCurveTimeline.__slots__ = [
    'super',
    'curves',
]
struct_spCurveTimeline._fields_ = [
    ('super', struct_spTimeline),
    ('curves', POINTER(c_float)),
]

spCurveTimeline = struct_spCurveTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 15

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 22
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

spBaseTimeline = struct_spBaseTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 22

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 29
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

spColorTimeline = struct_spColorTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 29

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 36
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

spTwoColorTimeline = struct_spTwoColorTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 36

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 44
class struct_spAttachmentTimeline(Structure):
    pass

struct_spAttachmentTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'slotIndex',
    'attachmentNames',
]
struct_spAttachmentTimeline._fields_ = [
    ('super', struct_spTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('slotIndex', c_int),
    ('attachmentNames', POINTER(POINTER(c_char))),
]

spAttachmentTimeline = struct_spAttachmentTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 44

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 152
class struct_spEvent(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 51
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

spEventTimeline = struct_spEventTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 51

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 59
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

spDrawOrderTimeline = struct_spDrawOrderTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 59

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 196
class struct_spAttachment(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 69
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

spDeformTimeline = struct_spDeformTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 69

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 76
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

spIkConstraintTimeline = struct_spIkConstraintTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 76

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 83
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

spTransformConstraintTimeline = struct_spTransformConstraintTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 83

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 90
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

spPathConstraintPositionTimeline = struct_spPathConstraintPositionTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 90

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 97
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

spPathConstraintSpacingTimeline = struct_spPathConstraintSpacingTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 97

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 104
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

spPathConstraintMixTimeline = struct_spPathConstraintMixTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 104

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 114
class struct_spEventData(Structure):
    pass

struct_spEventData.__slots__ = [
    'name',
    'intValue',
    'floatValue',
    'stringValue',
    'audioPath',
    'volume',
    'balance',
]
struct_spEventData._fields_ = [
    ('name', String),
    ('intValue', c_int),
    ('floatValue', c_float),
    ('stringValue', String),
    ('audioPath', String),
    ('volume', c_float),
    ('balance', c_float),
]

spEventData = struct_spEventData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 114

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 363
class struct_spBoneData(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 167
class struct_spColor(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 124
class struct_spSlotData(Structure):
    pass

struct_spSlotData.__slots__ = [
    'index',
    'name',
    'boneData',
    'attachmentName',
    'color',
    'darkColor',
    'blendMode',
]
struct_spSlotData._fields_ = [
    ('index', c_int),
    ('name', String),
    ('boneData', POINTER(struct_spBoneData)),
    ('attachmentName', String),
    ('color', struct_spColor),
    ('darkColor', POINTER(struct_spColor)),
    ('blendMode', c_int),
]

spSlotData = struct_spSlotData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 124

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 171
class struct_spTriangulator(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 128
class struct_spFloatArray(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 132
class struct_spUnsignedShortArray(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 162
class struct_spClippingAttachment(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 135
class struct_spArrayFloatArray(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 136
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

spSkeletonClipping = struct_spSkeletonClipping# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 136

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 139
class struct_spVertexAttachment(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 144
class struct_spPathAttachment(Structure):
    pass

struct_spPathAttachment.__slots__ = [
    'super',
    'lengthsLength',
    'lengths',
    'closed',
    'constantSpeed',
]
struct_spPathAttachment._fields_ = [
    ('super', struct_spVertexAttachment),
    ('lengthsLength', c_int),
    ('lengths', POINTER(c_float)),
    ('closed', c_int),
    ('constantSpeed', c_int),
]

spPathAttachment = struct_spPathAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 144

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 150
class struct_spPointAttachment(Structure):
    pass

struct_spPointAttachment.__slots__ = [
    'super',
    'x',
    'y',
    'rotation',
    'color',
]
struct_spPointAttachment._fields_ = [
    ('super', struct_spAttachment),
    ('x', c_float),
    ('y', c_float),
    ('rotation', c_float),
    ('color', struct_spColor),
]

spPointAttachment = struct_spPointAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 150

struct_spEvent.__slots__ = [
    'data',
    'time',
    'intValue',
    'floatValue',
    'stringValue',
    'volume',
    'balance',
]
struct_spEvent._fields_ = [
    ('data', POINTER(spEventData)),
    ('time', c_float),
    ('intValue', c_int),
    ('floatValue', c_float),
    ('stringValue', String),
    ('volume', c_float),
    ('balance', c_float),
]

spEvent = struct_spEvent# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 160

struct_spClippingAttachment.__slots__ = [
    'super',
    'endSlot',
]
struct_spClippingAttachment._fields_ = [
    ('super', struct_spVertexAttachment),
    ('endSlot', POINTER(spSlotData)),
]

spClippingAttachment = struct_spClippingAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 165

struct_spColor.__slots__ = [
    'r',
    'g',
    'b',
    'a',
]
struct_spColor._fields_ = [
    ('r', c_float),
    ('g', c_float),
    ('b', c_float),
    ('a', c_float),
]

spColor = struct_spColor# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 169

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 173
class struct_spArrayShortArray(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 174
class struct_spShortArray(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 175
class struct_spIntArray(Structure):
    pass

struct_spTriangulator.__slots__ = [
    'convexPolygons',
    'convexPolygonsIndices',
    'indicesArray',
    'isConcaveArray',
    'triangles',
    'polygonPool',
    'polygonIndicesPool',
]
struct_spTriangulator._fields_ = [
    ('convexPolygons', POINTER(struct_spArrayFloatArray)),
    ('convexPolygonsIndices', POINTER(struct_spArrayShortArray)),
    ('indicesArray', POINTER(struct_spShortArray)),
    ('isConcaveArray', POINTER(struct_spIntArray)),
    ('triangles', POINTER(struct_spShortArray)),
    ('polygonPool', POINTER(struct_spArrayFloatArray)),
    ('polygonIndicesPool', POINTER(struct_spArrayShortArray)),
]

spTriangulator = struct_spTriangulator# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 179

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 194
class struct_spRegionAttachment(Structure):
    pass

struct_spRegionAttachment.__slots__ = [
    'super',
    'path',
    'x',
    'y',
    'scaleX',
    'scaleY',
    'rotation',
    'width',
    'height',
    'color',
    'rendererObject',
    'regionOffsetX',
    'regionOffsetY',
    'regionWidth',
    'regionHeight',
    'regionOriginalWidth',
    'regionOriginalHeight',
    'offset',
    'uvs',
]
struct_spRegionAttachment._fields_ = [
    ('super', struct_spAttachment),
    ('path', String),
    ('x', c_float),
    ('y', c_float),
    ('scaleX', c_float),
    ('scaleY', c_float),
    ('rotation', c_float),
    ('width', c_float),
    ('height', c_float),
    ('color', spColor),
    ('rendererObject', POINTER(None)),
    ('regionOffsetX', c_int),
    ('regionOffsetY', c_int),
    ('regionWidth', c_int),
    ('regionHeight', c_int),
    ('regionOriginalWidth', c_int),
    ('regionOriginalHeight', c_int),
    ('offset', c_float * int(8)),
    ('uvs', c_float * int(8)),
]

spRegionAttachment = struct_spRegionAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 194

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 267
class struct_spAttachmentLoader(Structure):
    pass

struct_spAttachment.__slots__ = [
    'name',
    'type',
    'vtable',
    'refCount',
    'attachmentLoader',
]
struct_spAttachment._fields_ = [
    ('name', String),
    ('type', c_int),
    ('vtable', POINTER(None)),
    ('refCount', c_int),
    ('attachmentLoader', POINTER(struct_spAttachmentLoader)),
]

spAttachment = struct_spAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 202

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 205
class struct_spTransformConstraintData(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 207
class struct_spBone(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 211
class struct_spTransformConstraint(Structure):
    pass

struct_spTransformConstraint.__slots__ = [
    'data',
    'bonesCount',
    'bones',
    'target',
    'rotateMix',
    'translateMix',
    'scaleMix',
    'shearMix',
    'active',
]
struct_spTransformConstraint._fields_ = [
    ('data', POINTER(struct_spTransformConstraintData)),
    ('bonesCount', c_int),
    ('bones', POINTER(POINTER(struct_spBone))),
    ('target', POINTER(struct_spBone)),
    ('rotateMix', c_float),
    ('translateMix', c_float),
    ('scaleMix', c_float),
    ('shearMix', c_float),
    ('active', c_int),
]

spTransformConstraint = struct_spTransformConstraint# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 211

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 217
class struct_spSkeletonJson(Structure):
    pass

struct_spSkeletonJson.__slots__ = [
    'scale',
    'attachmentLoader',
    'error',
]
struct_spSkeletonJson._fields_ = [
    ('scale', c_float),
    ('attachmentLoader', POINTER(struct_spAttachmentLoader)),
    ('error', String),
]

spSkeletonJson = struct_spSkeletonJson# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 217

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 232
class struct_spIkConstraintData(Structure):
    pass

struct_spIkConstraintData.__slots__ = [
    'name',
    'order',
    'skinRequired',
    'bonesCount',
    'bones',
    'target',
    'bendDirection',
    'compress',
    'stretch',
    'uniform',
    'mix',
    'softness',
]
struct_spIkConstraintData._fields_ = [
    ('name', String),
    ('order', c_int),
    ('skinRequired', c_int),
    ('bonesCount', c_int),
    ('bones', POINTER(POINTER(struct_spBoneData))),
    ('target', POINTER(struct_spBoneData)),
    ('bendDirection', c_int),
    ('compress', c_int),
    ('stretch', c_int),
    ('uniform', c_int),
    ('mix', c_float),
    ('softness', c_float),
]

spIkConstraintData = struct_spIkConstraintData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 232

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 235
class struct_spSkeletonData(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 238
class struct_spAnimationStateData(Structure):
    pass

struct_spAnimationStateData.__slots__ = [
    'skeletonData',
    'defaultMix',
    'entries',
]
struct_spAnimationStateData._fields_ = [
    ('skeletonData', POINTER(struct_spSkeletonData)),
    ('defaultMix', c_float),
    ('entries', POINTER(None)),
]

spAnimationStateData = struct_spAnimationStateData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 238

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 248
class struct_spSlot(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 252
class struct_spIkConstraint(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 258
class struct_spPathConstraint(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 274
class struct_spSkin(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 265
class struct_spSkeleton(Structure):
    pass

struct_spSkeleton.__slots__ = [
    'data',
    'bonesCount',
    'bones',
    'root',
    'slotsCount',
    'slots',
    'drawOrder',
    'ikConstraintsCount',
    'ikConstraints',
    'transformConstraintsCount',
    'transformConstraints',
    'pathConstraintsCount',
    'pathConstraints',
    'skin',
    'color',
    'time',
    'scaleX',
    'scaleY',
    'x',
    'y',
]
struct_spSkeleton._fields_ = [
    ('data', POINTER(struct_spSkeletonData)),
    ('bonesCount', c_int),
    ('bones', POINTER(POINTER(struct_spBone))),
    ('root', POINTER(struct_spBone)),
    ('slotsCount', c_int),
    ('slots', POINTER(POINTER(struct_spSlot))),
    ('drawOrder', POINTER(POINTER(struct_spSlot))),
    ('ikConstraintsCount', c_int),
    ('ikConstraints', POINTER(POINTER(struct_spIkConstraint))),
    ('transformConstraintsCount', c_int),
    ('transformConstraints', POINTER(POINTER(struct_spTransformConstraint))),
    ('pathConstraintsCount', c_int),
    ('pathConstraints', POINTER(POINTER(struct_spPathConstraint))),
    ('skin', POINTER(struct_spSkin)),
    ('color', spColor),
    ('time', c_float),
    ('scaleX', c_float),
    ('scaleY', c_float),
    ('x', c_float),
    ('y', c_float),
]

spSkeleton = struct_spSkeleton# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 265

struct_spAttachmentLoader.__slots__ = [
    'error1',
    'error2',
    'vtable',
]
struct_spAttachmentLoader._fields_ = [
    ('error1', String),
    ('error2', String),
    ('vtable', POINTER(None)),
]

spAttachmentLoader = struct_spAttachmentLoader# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 272

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 277
class struct_spBoneDataArray(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 278
class struct_spIkConstraintDataArray(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 279
class struct_spTransformConstraintDataArray(Structure):
    pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 280
class struct_spPathConstraintDataArray(Structure):
    pass

struct_spSkin.__slots__ = [
    'name',
    'bones',
    'ikConstraints',
    'transformConstraints',
    'pathConstraints',
]
struct_spSkin._fields_ = [
    ('name', String),
    ('bones', POINTER(struct_spBoneDataArray)),
    ('ikConstraints', POINTER(struct_spIkConstraintDataArray)),
    ('transformConstraints', POINTER(struct_spTransformConstraintDataArray)),
    ('pathConstraints', POINTER(struct_spPathConstraintDataArray)),
]

spSkin = struct_spSkin# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 281

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 287
class struct_spVertexEffect(Structure):
    pass

struct_spVertexEffect.__slots__ = [
    'begin',
    'transform',
    'end',
]
struct_spVertexEffect._fields_ = [
    ('begin', CFUNCTYPE(UNCHECKED(None), POINTER(None))),
    ('transform', CFUNCTYPE(UNCHECKED(None), POINTER(None), POINTER(c_float), c_int)),
    ('end', CFUNCTYPE(UNCHECKED(None), POINTER(None))),
]

spVertexEffect = struct_spVertexEffect# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 287

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 293
class struct_spJitterVertexEffect(Structure):
    pass

struct_spJitterVertexEffect.__slots__ = [
    'super',
    'jitterX',
    'jitterY',
]
struct_spJitterVertexEffect._fields_ = [
    ('super', spVertexEffect),
    ('jitterX', c_float),
    ('jitterY', c_float),
]

spJitterVertexEffect = struct_spJitterVertexEffect# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 293

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 303
class struct_spSwirlVertexEffect(Structure):
    pass

struct_spSwirlVertexEffect.__slots__ = [
    'super',
    'centerX',
    'centerY',
    'radius',
    'angle',
    'worldX',
    'worldY',
]
struct_spSwirlVertexEffect._fields_ = [
    ('super', spVertexEffect),
    ('centerX', c_float),
    ('centerY', c_float),
    ('radius', c_float),
    ('angle', c_float),
    ('worldX', c_float),
    ('worldY', c_float),
]

spSwirlVertexEffect = struct_spSwirlVertexEffect# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 303

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 309
class struct_spSkeletonBinary(Structure):
    pass

struct_spSkeletonBinary.__slots__ = [
    'scale',
    'attachmentLoader',
    'error',
]
struct_spSkeletonBinary._fields_ = [
    ('scale', c_float),
    ('attachmentLoader', POINTER(spAttachmentLoader)),
    ('error', String),
]

spSkeletonBinary = struct_spSkeletonBinary# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 309

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 341
for _lib in _libs.values():
    try:
        pathConstraintsCount = (c_int).in_dll(_lib, "pathConstraintsCount")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 361
class struct_spPathConstraintData(Structure):
    pass

struct_spPathConstraintData.__slots__ = [
    'name',
    'order',
    'skinRequired',
    'bonesCount',
    'bones',
    'target',
    'positionMode',
    'spacingMode',
    'rotateMode',
    'rotation',
    'position',
    'spacing',
    'mixRotate',
    'mixX',
    'mixY',
]
struct_spPathConstraintData._fields_ = [
    ('name', String),
    ('order', c_int),
    ('skinRequired', c_int),
    ('bonesCount', c_int),
    ('bones', POINTER(POINTER(struct_spBoneData))),
    ('target', POINTER(struct_spSlotData)),
    ('positionMode', c_int),
    ('spacingMode', c_int),
    ('rotateMode', c_int),
    ('rotation', c_float),
    ('position', c_float),
    ('spacing', c_float),
    ('mixRotate', c_float),
    ('mixX', c_float),
    ('mixY', c_float),
]

spPathConstraintData = struct_spPathConstraintData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 361

struct_spBoneData.__slots__ = [
    'name',
    'parent',
    'length',
    'x',
    'y',
    'rotation',
    'scaleX',
    'scaleY',
    'shearX',
    'shearY',
    'transformMode',
    'skinRequired',
    'color',
]
struct_spBoneData._fields_ = [
    ('name', String),
    ('parent', POINTER(struct_spBoneData)),
    ('length', c_float),
    ('x', c_float),
    ('y', c_float),
    ('rotation', c_float),
    ('scaleX', c_float),
    ('scaleY', c_float),
    ('shearX', c_float),
    ('shearY', c_float),
    ('transformMode', c_int),
    ('skinRequired', c_int),
    ('color', c_float * int(4)),
]

spBoneData = struct_spBoneData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 374

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 381
for _lib in _libs.values():
    try:
        childrenCount = (c_int).in_dll(_lib, "childrenCount")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 383
for _lib in _libs.values():
    try:
        x = (c_float).in_dll(_lib, "x")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 383
for _lib in _libs.values():
    try:
        y = (c_float).in_dll(_lib, "y")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 384
for _lib in _libs.values():
    try:
        rotation = (c_float).in_dll(_lib, "rotation")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 385
for _lib in _libs.values():
    try:
        scaleX = (c_float).in_dll(_lib, "scaleX")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 385
for _lib in _libs.values():
    try:
        scaleY = (c_float).in_dll(_lib, "scaleY")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 386
for _lib in _libs.values():
    try:
        shearX = (c_float).in_dll(_lib, "shearX")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 386
for _lib in _libs.values():
    try:
        shearY = (c_float).in_dll(_lib, "shearY")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 388
for _lib in _libs.values():
    try:
        ax = (c_float).in_dll(_lib, "ax")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 388
for _lib in _libs.values():
    try:
        ay = (c_float).in_dll(_lib, "ay")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 389
for _lib in _libs.values():
    try:
        arotation = (c_float).in_dll(_lib, "arotation")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 390
for _lib in _libs.values():
    try:
        ascaleX = (c_float).in_dll(_lib, "ascaleX")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 390
for _lib in _libs.values():
    try:
        ascaleY = (c_float).in_dll(_lib, "ascaleY")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 391
for _lib in _libs.values():
    try:
        ashearX = (c_float).in_dll(_lib, "ashearX")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 391
for _lib in _libs.values():
    try:
        ashearY = (c_float).in_dll(_lib, "ashearY")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 393
for _lib in _libs.values():
    try:
        appliedValid = (c_float).in_dll(_lib, "appliedValid")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 395
for _lib in _libs.values():
    try:
        worldX = (c_float).in_dll(_lib, "worldX")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 395
for _lib in _libs.values():
    try:
        worldY = (c_float).in_dll(_lib, "worldY")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 396
for _lib in _libs.values():
    try:
        worldSignX = (c_float).in_dll(_lib, "worldSignX")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 396
for _lib in _libs.values():
    try:
        worldSignY = (c_float).in_dll(_lib, "worldSignY")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 397
for _lib in _libs.values():
    try:
        a = (c_float).in_dll(_lib, "a")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 397
for _lib in _libs.values():
    try:
        b = (c_float).in_dll(_lib, "b")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 397
for _lib in _libs.values():
    try:
        worldA = (c_float).in_dll(_lib, "worldA")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 397
for _lib in _libs.values():
    try:
        worldB = (c_float).in_dll(_lib, "worldB")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 398
for _lib in _libs.values():
    try:
        c = (c_float).in_dll(_lib, "c")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 398
for _lib in _libs.values():
    try:
        d = (c_float).in_dll(_lib, "d")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 398
for _lib in _libs.values():
    try:
        worldC = (c_float).in_dll(_lib, "worldC")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 398
for _lib in _libs.values():
    try:
        worldD = (c_float).in_dll(_lib, "worldD")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 404
for _lib in _libs.values():
    try:
        attachment = (POINTER(struct_spAttachment)).in_dll(_lib, "attachment")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 405
for _lib in _libs.values():
    try:
        r = (c_float).in_dll(_lib, "r")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 405
for _lib in _libs.values():
    try:
        g = (c_float).in_dll(_lib, "g")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 405
for _lib in _libs.values():
    try:
        b = (c_float).in_dll(_lib, "b")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 405
for _lib in _libs.values():
    try:
        a = (c_float).in_dll(_lib, "a")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 406
for _lib in _libs.values():
    try:
        r2 = (c_float).in_dll(_lib, "r2")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 406
for _lib in _libs.values():
    try:
        g2 = (c_float).in_dll(_lib, "g2")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 406
for _lib in _libs.values():
    try:
        b2 = (c_float).in_dll(_lib, "b2")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 406
for _lib in _libs.values():
    try:
        a2 = (c_float).in_dll(_lib, "a2")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 407
for _lib in _libs.values():
    try:
        attachmentTime = (c_float).in_dll(_lib, "attachmentTime")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 408
for _lib in _libs.values():
    try:
        attachmentState = (c_int).in_dll(_lib, "attachmentState")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 409
for _lib in _libs.values():
    try:
        darkColor = (c_int).in_dll(_lib, "darkColor")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 419
for _lib in _libs.values():
    try:
        positionMode = (c_int).in_dll(_lib, "positionMode")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 420
for _lib in _libs.values():
    try:
        spacingMode = (c_int).in_dll(_lib, "spacingMode")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 421
for _lib in _libs.values():
    try:
        rotateMode = (c_int).in_dll(_lib, "rotateMode")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 423
for _lib in _libs.values():
    try:
        position = (c_float).in_dll(_lib, "position")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 424
for _lib in _libs.values():
    try:
        spacing = (c_float).in_dll(_lib, "spacing")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 425
for _lib in _libs.values():
    try:
        rotateMix = (c_float).in_dll(_lib, "rotateMix")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 426
for _lib in _libs.values():
    try:
        translateMix = (c_float).in_dll(_lib, "translateMix")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 428
for _lib in _libs.values():
    try:
        spaces = (POINTER(c_float)).in_dll(_lib, "spaces")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 429
for _lib in _libs.values():
    try:
        positions = (POINTER(c_float)).in_dll(_lib, "positions")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 430
for _lib in _libs.values():
    try:
        worldLengths = (POINTER(c_float)).in_dll(_lib, "worldLengths")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 431
for _lib in _libs.values():
    try:
        curves = (POINTER(c_float)).in_dll(_lib, "curves")
        break
    except:
        pass

# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 432
for _lib in _libs.values():
    try:
        segments = (POINTER(c_float)).in_dll(_lib, "segments")
        break
    except:
        pass

struct_spTimeline.__slots__ = [
    'propertyId',
    'apply',
]
struct_spTimeline._fields_ = [
    ('propertyId', c_int),
    ('apply', CFUNCTYPE(UNCHECKED(None), POINTER(None), c_float, c_float, POINTER(c_float), c_float, c_float, c_int, c_int, POINTER(None))),
]

spTimeline = struct_spTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 438

spTimeline = struct_spTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 435

spAnimation = struct_spAnimation# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 10

spCurveTimeline = struct_spCurveTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 15

spBaseTimeline = struct_spBaseTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 22

spColorTimeline = struct_spColorTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 29

spTwoColorTimeline = struct_spTwoColorTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 36

spAttachmentTimeline = struct_spAttachmentTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 44

spEvent = struct_spEvent# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 152

spEventTimeline = struct_spEventTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 51

spDrawOrderTimeline = struct_spDrawOrderTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 59

spAttachment = struct_spAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 196

spDeformTimeline = struct_spDeformTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 69

spIkConstraintTimeline = struct_spIkConstraintTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 76

spTransformConstraintTimeline = struct_spTransformConstraintTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 83

spPathConstraintPositionTimeline = struct_spPathConstraintPositionTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 90

spPathConstraintSpacingTimeline = struct_spPathConstraintSpacingTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 97

spPathConstraintMixTimeline = struct_spPathConstraintMixTimeline# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 104

spEventData = struct_spEventData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 114

spBoneData = struct_spBoneData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 363

spColor = struct_spColor# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 167

spSlotData = struct_spSlotData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 124

spTriangulator = struct_spTriangulator# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 171

spFloatArray = struct_spFloatArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 128

spUnsignedShortArray = struct_spUnsignedShortArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 132

spClippingAttachment = struct_spClippingAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 162

spArrayFloatArray = struct_spArrayFloatArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 135

spSkeletonClipping = struct_spSkeletonClipping# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 136

spVertexAttachment = struct_spVertexAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 139

spPathAttachment = struct_spPathAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 144

spPointAttachment = struct_spPointAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 150

spArrayShortArray = struct_spArrayShortArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 173

spShortArray = struct_spShortArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 174

spIntArray = struct_spIntArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 175

spRegionAttachment = struct_spRegionAttachment# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 194

spAttachmentLoader = struct_spAttachmentLoader# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 267

spTransformConstraintData = struct_spTransformConstraintData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 205

spBone = struct_spBone# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 207

spTransformConstraint = struct_spTransformConstraint# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 211

spSkeletonJson = struct_spSkeletonJson# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 217

spIkConstraintData = struct_spIkConstraintData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 232

spSkeletonData = struct_spSkeletonData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 235

spAnimationStateData = struct_spAnimationStateData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 238

spSlot = struct_spSlot# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 248

spIkConstraint = struct_spIkConstraint# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 252

spPathConstraint = struct_spPathConstraint# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 258

spSkin = struct_spSkin# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 274

spSkeleton = struct_spSkeleton# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 265

spBoneDataArray = struct_spBoneDataArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 277

spIkConstraintDataArray = struct_spIkConstraintDataArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 278

spTransformConstraintDataArray = struct_spTransformConstraintDataArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 279

spPathConstraintDataArray = struct_spPathConstraintDataArray# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 280

spVertexEffect = struct_spVertexEffect# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 287

spJitterVertexEffect = struct_spJitterVertexEffect# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 293

spSwirlVertexEffect = struct_spSwirlVertexEffect# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 303

spSkeletonBinary = struct_spSkeletonBinary# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 309

spPathConstraintData = struct_spPathConstraintData# /Users/michelleyan/Downloads/sp/spine-python/manual_binding.h: 361

# No inserted files

# No prefix-stripping

