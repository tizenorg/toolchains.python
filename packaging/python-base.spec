Name:           python-base
Version:        2.7.3
Release:        0
License:        Python-2.0
Summary:        Python Interpreter base package
Url:            http://www.python.org/
Group:          Development/Languages/Python
%define         tarversion %{version}
%define         tarname Python-%{tarversion}
Source0:        %{tarname}.tar.bz2
Source1:        macros.python
Source4:        distutils.cfg
Source5:        _local.pth
Source1001:     python.manifest
# COMMON-PATCH-BEGIN
Patch1:         python-2.7-dirs.patch
Patch2:         python-distutils-rpm-8.patch
Patch3:         python-2.7.3rc2-multilib.patch
Patch4:         python-2.5.1-sqlite.patch
Patch5:         python-2.7.3rc2-canonicalize2.patch
Patch6:         python-2.7rc2-configure.patch
Patch7:         python-2.6-gettext-plurals.patch
Patch8:         python-2.6b3-curses-panel.patch
Patch9:         python-2.7.1-distutils_test_path.patch
Patch12:        http://psf.upfronthosting.co.za/roundup/tracker/file19029/python-test_structmembers.patch
Patch13:        python-2.7.2-fix_date_time_compiler.patch
Patch16:        pypirc-secure.diff
Patch17:        remove-static-libpython.diff
Patch18:        python-2.7.3-ssl_ca_path.patch
# COMMON-PATCH-END
%define         python_version    %(echo %{tarversion} | head -c 3)
BuildRequires:  automake
BuildRequires:  fdupes
BuildRequires:  pkg-config
BuildRequires:  zlib-devel
BuildRequires:  bzip2-devel

%description
Python is an interpreted, object-oriented programming language, and is
often compared to Tcl, Perl, Scheme, or Java.  You can find an overview
of Python in the documentation and tutorials included in the python-doc
(HTML) or python-doc-pdf (PDF) packages.

This package contains all of stand-alone Python files, minus binary
modules that would pull in extra dependencies.

%package -n python-devel
Summary:        Include Files and Libraries Mandatory for Building Python Modules
Group:          Development/Languages/Python
Requires:       glibc-devel
Requires:       python-base = %{version}

%description -n python-devel
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.

This package contains header files, a static library, and development
tools for building Python modules, extending the Python interpreter or
embedding Python in applications.

%package -n python-xml
Summary:        A Python XML Interface
Group:          Development/Libraries/Python
Requires:       python-base = %{version}
# pyxml used to live out of tree
Provides:       pyxml = 0.8.5
Obsoletes:      pyxml < 0.8.5

%description -n python-xml
The expat module is a Python interface to the expat XML parser. Since
Python2.x, it is part of the core Python distribution.

%package -n libpython
Summary:        Python Interpreter shared library
Group:          Development/Languages/Python

%description -n libpython
Python is an interpreted, object-oriented programming language, and is
often compared to Tcl, Perl, Scheme, or Java.  You can find an overview
of Python in the documentation and tutorials included in the python-doc
(HTML) or python-doc-pdf (PDF) packages.

This package contains libpython2.6 shared library for embedding in
other applications.

%prep
%setup -q -n %{tarname}
# patching
# COMMON-PREP-BEGIN
%patch1 -p1
%patch2 -p1
%patch3
%patch4
%patch5
%patch6
%patch7
%patch8
%patch9 -p1
%patch12
%patch13
#skip test_io test for ppc,ppc64 as it broken.
%patch16 -p1
%patch17
%patch18
# COMMON-PREP-END

# drop Autoconf version requirement
sed -i 's/^version_required/dnl version_required/' configure.in

%build
cp %{S:1001} .
export OPT="%{optflags}"

autoreconf -f -i . # Modules/_ctypes/libffi

# provide a stable timestamp
touch -r %{SOURCE0} Makefile.pre.in

# prevent make from trying to rebuild asdl stuff, which requires existing
# python installation
touch Parser/asdl* Python/Python-ast.c Include/Python-ast.h

%configure \
    --docdir=%{_docdir}/python \
    --with-fpectl \
    --enable-ipv6 \
    --enable-shared \
    --enable-unicode=ucs4

LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH \
    make %{?_smp_mflags} profile-opt


%install
# replace rest of /usr/local/bin/python or /usr/bin/python2.5 with /usr/bin/python
find . -wholename "./Parser" -prune -o -name '*.py' -type f -print0 | xargs -0 grep -lE '^#! *(/usr/.*bin/(env +)?)?python' | xargs sed -r -i -e '1s@^#![[:space:]]*(/usr/(local/)?bin/(env +)?)?python([0-9]+\.[0-9]+)?@#!/usr/bin/python@'
# the grep inbetween makes it much faster
########################################
# install it
########################################
%make_install OPT="%{optflags} -fPIC"
# install site-specific tweaks
#ln -s python%{python_version} %{buildroot}%{_bindir}/python2
install -m 644 %{SOURCE4} %{buildroot}%{_libdir}/python%{python_version}/distutils
install -m 644 %{SOURCE5} %{buildroot}%{_libdir}/python%{python_version}/site-packages
install -d -m 755 %{buildroot}%{_sysconfdir}/rpm
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/rpm
# make sure /usr/lib/python/site-packages exists even on lib64 machines
mkdir -p %{buildroot}%{_prefix}/lib/python%{python_version}/site-packages
########################################
# some cleanups
########################################
# remove hard links and replace them with symlinks
for dir in bin include %{_lib} ; do
    rm -f %{buildroot}/%{_prefix}/$dir/python
    ln -s python%{python_version} %{buildroot}/%{_prefix}/$dir/python
done
CLEANUP_DIR="%{buildroot}%{_libdir}/python%{python_version}"
# don't distribute precompiled windows installers (duh)
rm -f $CLEANUP_DIR/distutils/command/*.exe
# kill imageop.so and audioop.so, they are rarely used and insecure
rm -f $CLEANUP_DIR/lib-dynload/imageop.so
rm -f $CLEANUP_DIR/lib-dynload/audioop.so
# link shared library instead of static library that tools expect
ln -s ../../libpython%{python_version}.so %{buildroot}%{_libdir}/python%{python_version}/config/libpython%{python_version}.so
# remove various things that don't need to be in python-base
rm %{buildroot}%{_bindir}/idle
rm -rf $CLEANUP_DIR/{curses,bsddb,idlelib,lib-tk,sqlite3}
rm $CLEANUP_DIR/ssl.py*
#        does not work without _ssl.so anyway
# replace duplicate .pyo/.pyc with hardlinks
%fdupes %{buildroot}/%{_libdir}/python%{python_version}
########################################
# documentation
########################################
export PDOCS=%{buildroot}%{_docdir}/%{name}
install -d -m 755 $PDOCS
install -c -m 644 LICENSE                           $PDOCS/
install -c -m 644 README                            $PDOCS/
ln -s python%{python_version}.1.gz %{buildroot}%{_mandir}/man1/python.1.gz
########################################
# devel
########################################
# install Makefile.pre.in and Makefile.pre
cp Makefile Makefile.pre.in Makefile.pre %{buildroot}%{_libdir}/python%{python_version}/config/

%post -n libpython -p /sbin/ldconfig

%postun -n libpython -p /sbin/ldconfig

%files -n python-devel
%manifest python.manifest
%defattr(-, root, root)
%{_libdir}/python%{python_version}/config/*
%exclude %{_libdir}/python%{python_version}/config/Setup
%exclude %{_libdir}/python%{python_version}/config/Makefile
%defattr(644, root, root, 755)
%{_libdir}/libpython*.so
%{_libdir}/pkgconfig/python-%{python_version}.pc
%{_libdir}/pkgconfig/python.pc
%{_libdir}/pkgconfig/python2.pc
%{_includedir}/python*
%exclude %{_includedir}/python%{python_version}/pyconfig.h
%{_libdir}/python%{python_version}/test
%defattr(755, root, root)
%{_bindir}/python-config
%{_bindir}/python2-config
%{_bindir}/python%{python_version}-config

%files -n python-xml
%manifest python.manifest
%defattr(644, root, root, 755)
%{_libdir}/python%{python_version}/xml
%{_libdir}/python%{python_version}/lib-dynload/pyexpat.so

%files -n libpython
%manifest python.manifest
%defattr(644, root, root)
%{_libdir}/libpython*.so.*

%files
%manifest python.manifest
%defattr(644, root, root, 755)
%config %{_sysconfdir}/rpm/macros.python
%dir %{_docdir}/%{name}
%doc %{_docdir}/%{name}/README
%doc %{_docdir}/%{name}/LICENSE
%doc %{_mandir}/man1/python.1*
%doc %{_mandir}/man1/python%{python_version}.1*
%dir %{_includedir}/python%{python_version}
%{_includedir}/python%{python_version}/pyconfig.h
%{_libdir}/python
%dir %{_prefix}/lib/python%{python_version}
%dir %{_prefix}/lib/python%{python_version}/site-packages
%dir %{_libdir}/python%{python_version}
%dir %{_libdir}/python%{python_version}/config
%{_libdir}/python%{python_version}/config/Setup
%{_libdir}/python%{python_version}/config/Makefile
%{_libdir}/python%{python_version}/*.*
%{_libdir}/python%{python_version}/compiler
%{_libdir}/python%{python_version}/ctypes
%{_libdir}/python%{python_version}/distutils
%{_libdir}/python%{python_version}/email
%{_libdir}/python%{python_version}/encodings
%{_libdir}/python%{python_version}/hotshot
%{_libdir}/python%{python_version}/importlib
%{_libdir}/python%{python_version}/json
%{_libdir}/python%{python_version}/lib2to3
%{_libdir}/python%{python_version}/logging
%{_libdir}/python%{python_version}/multiprocessing
%{_libdir}/python%{python_version}/plat-*
%{_libdir}/python%{python_version}/pydoc_data
%{_libdir}/python%{python_version}/unittest
%{_libdir}/python%{python_version}/wsgiref
%dir %{_libdir}/python%{python_version}/site-packages
%{_libdir}/python%{python_version}/site-packages/README
%{_libdir}/python%{python_version}/site-packages/_local.pth
%dir %{_libdir}/python%{python_version}/lib-dynload
%{_libdir}/python%{python_version}/lib-dynload/_bisect.so
%{_libdir}/python%{python_version}/lib-dynload/_csv.so
%{_libdir}/python%{python_version}/lib-dynload/_collections.so
%{_libdir}/python%{python_version}/lib-dynload/_ctypes.so
%{_libdir}/python%{python_version}/lib-dynload/_ctypes_test.so
%{_libdir}/python%{python_version}/lib-dynload/_elementtree.so
%{_libdir}/python%{python_version}/lib-dynload/_functools.so
%{_libdir}/python%{python_version}/lib-dynload/_heapq.so
%{_libdir}/python%{python_version}/lib-dynload/_hotshot.so
%{_libdir}/python%{python_version}/lib-dynload/_io.so
%{_libdir}/python%{python_version}/lib-dynload/_json.so
%{_libdir}/python%{python_version}/lib-dynload/_locale.so
%{_libdir}/python%{python_version}/lib-dynload/_lsprof.so
%{_libdir}/python%{python_version}/lib-dynload/_md5.so
%{_libdir}/python%{python_version}/lib-dynload/_multiprocessing.so
%{_libdir}/python%{python_version}/lib-dynload/_random.so
%{_libdir}/python%{python_version}/lib-dynload/_sha.so
%{_libdir}/python%{python_version}/lib-dynload/_sha256.so
%{_libdir}/python%{python_version}/lib-dynload/_sha512.so
%{_libdir}/python%{python_version}/lib-dynload/_socket.so
%{_libdir}/python%{python_version}/lib-dynload/_struct.so
%{_libdir}/python%{python_version}/lib-dynload/_testcapi.so
%{_libdir}/python%{python_version}/lib-dynload/array.so
%{_libdir}/python%{python_version}/lib-dynload/binascii.so
%{_libdir}/python%{python_version}/lib-dynload/bz2.so
%{_libdir}/python%{python_version}/lib-dynload/cPickle.so
%{_libdir}/python%{python_version}/lib-dynload/cStringIO.so
%{_libdir}/python%{python_version}/lib-dynload/cmath.so
%{_libdir}/python%{python_version}/lib-dynload/crypt.so
%{_libdir}/python%{python_version}/lib-dynload/datetime.so
%{_libdir}/python%{python_version}/lib-dynload/fcntl.so
%{_libdir}/python%{python_version}/lib-dynload/future_builtins.so
%{_libdir}/python%{python_version}/lib-dynload/grp.so
%{_libdir}/python%{python_version}/lib-dynload/itertools.so
%{_libdir}/python%{python_version}/lib-dynload/linuxaudiodev.so
%{_libdir}/python%{python_version}/lib-dynload/math.so
%{_libdir}/python%{python_version}/lib-dynload/mmap.so
%{_libdir}/python%{python_version}/lib-dynload/nis.so
%{_libdir}/python%{python_version}/lib-dynload/operator.so
%{_libdir}/python%{python_version}/lib-dynload/ossaudiodev.so
%{_libdir}/python%{python_version}/lib-dynload/parser.so
%{_libdir}/python%{python_version}/lib-dynload/resource.so
%{_libdir}/python%{python_version}/lib-dynload/select.so
%{_libdir}/python%{python_version}/lib-dynload/spwd.so
%{_libdir}/python%{python_version}/lib-dynload/strop.so
%{_libdir}/python%{python_version}/lib-dynload/syslog.so
%{_libdir}/python%{python_version}/lib-dynload/termios.so
%{_libdir}/python%{python_version}/lib-dynload/time.so
%{_libdir}/python%{python_version}/lib-dynload/unicodedata.so
%{_libdir}/python%{python_version}/lib-dynload/zlib.so
%{_libdir}/python%{python_version}/lib-dynload/_codecs*.so
%{_libdir}/python%{python_version}/lib-dynload/_multibytecodec.so
%{_libdir}/python%{python_version}/lib-dynload/Python-%{tarversion}-py%{python_version}.egg-info
# these modules don't support 64-bit arches (disabled by setup.py)
%ifnarch x86_64
# requires sizeof(int) == sizeof(long) == sizeof(char*)
%{_libdir}/python%{python_version}/lib-dynload/dl.so
%endif
%attr(755, root, root) %{_bindir}/pydoc
%attr(755, root, root) %{_bindir}/python
%attr(755, root, root) %{_bindir}/python%{python_version}
%attr(755, root, root) %{_bindir}/smtpd.py
%{_bindir}/python2
%exclude %{_bindir}/2to3

