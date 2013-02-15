Name:           python
Version:        2.7.3
Release:        1
License:        Python-2.0
Summary:        Python Interpreter
Url:            http://www.python.org/
Group:          Development/Languages/Python
%define         tarversion %{version}
%define         tarname Python-%{tarversion}
Source0:        %{tarname}.tar.bz2
Source2:        pythonstart
Source3:        python.sh
Source4:        python.csh
Source1001:     %name.manifest
# !!!!!!!!!!!!!!
# do not add or edit patches here. please edit python-base.spec
# instead and run pre_checkin.sh
# !!!!!!!!!!!!!!
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
BuildRequires:  automake
BuildRequires:  db4-devel
BuildRequires:  fdupes
BuildRequires:  gmp-devel
BuildRequires:  bzip2-devel
BuildRequires:  openssl-devel
BuildRequires:  ncurses-devel
BuildRequires:  readline-devel
BuildRequires:  sqlite-devel
%define         python_version    %(echo %{tarversion} | head -c 3)
%define         idle_name         idle
Requires:       python-base = %{version}
Provides:       %{name} = %{python_version}
Obsoletes:      python-elementtree
Obsoletes:      python-nothreads
Obsoletes:      python-sqlite

%description
Python is an interpreted, object-oriented programming language, and is
often compared to Tcl, Perl, Scheme, or Java.  You can find an overview
of Python in the documentation and tutorials included in the python-doc
(HTML) or python-doc-pdf (PDF) packages.

If you want to install third party modules using distutils, you need to
install python-devel package.

%package curses
Summary:        Python Interface to the (N)Curses Library
Group:          Development/Libraries/Python
Requires:       python-base = %{version}
Obsoletes:      pyth_cur
Provides:       pyth_cur

%description curses
An easy to use interface to the (n)curses CUI library. CUI stands for
Console User Interface.


%prep
%setup -q -n %{tarname}
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

# remove newslist.py because of bad license
rm Demo/scripts/newslist.*

%build
cp %{S:1001} .
export OPT="%{optflags}"

autoreconf -f -i . # Modules/_ctypes/libffi
# prevent make from trying to rebuild asdl stuff, which requires existing
# python installation
touch Parser/asdl* Python/Python-ast.c Include/Python-ast.h

%configure \
    --docdir=%{_docdir}/python \
    --enable-ipv6 \
    --with-fpectl \
    --enable-shared \
    --enable-unicode=ucs4

make %{?_smp_mflags}

%install
# replace rest of /usr/local/bin/python or /usr/bin/python2.x with /usr/bin/python
find . -wholename "./Parser" -prune -o -name '*.py' -type f -print0 | xargs -0 grep -lE '^#! *(/usr/.*bin/(env +)?)?python' | xargs sed -r -i -e '1s@^#![[:space:]]*(/usr/(local/)?bin/(env +)?)?python([0-9]+\.[0-9]+)?@#!/usr/bin/python@'
# the grep inbetween makes it much faster
########################################
# install it
########################################
%make_install OPT="%{optflags} -fPIC"
########################################
# some cleanups
########################################
# remove hard links and replace them with symlinks
for dir in bin include %{_lib} ; do
    rm -f %{buildroot}/%{_prefix}/$dir/python
    ln -s python%{python_version} %{buildroot}/%{_prefix}/$dir/python
done
# kill imageop.so, it's insecure
rm -f %{buildroot}/%{_libdir}/python%{python_version}/lib-dynload/imageop.so
#cleanup for -base
rm %{buildroot}%{_bindir}/python%{python_version}
rm %{buildroot}%{_bindir}/python2
rm %{buildroot}%{_bindir}/python
rm %{buildroot}%{_bindir}/smtpd.py
rm %{buildroot}%{_bindir}/pydoc
rm %{buildroot}%{_bindir}/2to3
rm %{buildroot}%{_mandir}/man1/python*
rm %{buildroot}%{_libdir}/libpython*.so.*
rm %{buildroot}%{_libdir}/python
find %{buildroot}%{_libdir}/python%{python_version} -maxdepth 1 ! \( -name "ssl.py" \) -exec rm {} ";"
rm %{buildroot}%{_bindir}/python%{python_version}-config
rm %{buildroot}%{_bindir}/python2-config
rm %{buildroot}%{_bindir}/python-config
rm %{buildroot}%{_libdir}/pkgconfig/*
rm -rf %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/dbm.so
rm -r %{buildroot}%{_includedir}/python
rm -r %{buildroot}%{_includedir}/python%{python_version}
rm -r %{buildroot}%{_libdir}/python%{python_version}/compiler
rm -r %{buildroot}%{_libdir}/python%{python_version}/config
rm -r %{buildroot}%{_libdir}/python%{python_version}/ctypes
rm -r %{buildroot}%{_libdir}/python%{python_version}/distutils
rm -r %{buildroot}%{_libdir}/python%{python_version}/email
rm -r %{buildroot}%{_libdir}/python%{python_version}/encodings
rm -r %{buildroot}%{_libdir}/python%{python_version}/hotshot
rm -r %{buildroot}%{_libdir}/python%{python_version}/importlib
rm -r %{buildroot}%{_libdir}/python%{python_version}/json
rm -r %{buildroot}%{_libdir}/python%{python_version}/lib2to3
rm -r %{buildroot}%{_libdir}/python%{python_version}/logging
rm -r %{buildroot}%{_libdir}/python%{python_version}/multiprocessing
rm -r %{buildroot}%{_libdir}/python%{python_version}/plat-*
rm -r %{buildroot}%{_libdir}/python%{python_version}/pydoc_data
rm -r %{buildroot}%{_libdir}/python%{python_version}/test
rm -r %{buildroot}%{_libdir}/python%{python_version}/unittest
rm -r %{buildroot}%{_libdir}/python%{python_version}/wsgiref
rm -r %{buildroot}%{_libdir}/python%{python_version}/xml
rm %{buildroot}%{_libdir}/libpython%{python_version}.so
rm %{buildroot}%{_libdir}/python%{python_version}/site-packages/README
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_bisect.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_csv.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_collections.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_ctypes.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_ctypes_test.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_elementtree.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_functools.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_heapq.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_hotshot.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_io.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_json.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_locale.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_lsprof.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_multiprocessing.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_random.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_socket.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_struct.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_testcapi.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/array.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/binascii.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/bz2.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/cPickle.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/cStringIO.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/cmath.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/crypt.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/datetime.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/fcntl.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/future_builtins.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/grp.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/itertools.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/linuxaudiodev.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/math.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/mmap.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/nis.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/operator.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/ossaudiodev.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/parser.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/pyexpat.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/resource.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/select.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/spwd.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/strop.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/syslog.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/termios.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/time.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/unicodedata.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/zlib.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_codecs*.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/_multibytecodec.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/audioop.so
rm -f %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/dl.so
rm %{buildroot}%{_libdir}/python%{python_version}/lib-dynload/Python-%{tarversion}-py%{python_version}.egg-info
# replace duplicate .pyo/.pyc with hardlinks
%fdupes %{buildroot}/%{_libdir}/python%{python_version}
########################################
# documentation
########################################
export PDOCS=%{buildroot}%{_docdir}/%{name}
install -d -m 755 $PDOCS
install -c -m 644 LICENSE                           $PDOCS/
install -c -m 644 README                            $PDOCS/
########################################
# startup script
########################################
install -d -m 755 %{buildroot}%{_sysconfdir}/profile.d
install -m 644 %{SOURCE2} %{buildroot}/etc
install -m 644 %{SOURCE3} %{SOURCE4} %{buildroot}%{_sysconfdir}/profile.d

rm -rf %{buildroot}%{_bindir}/idle
rm -rf %{buildroot}%{_libdir}/python%{python_version}/idlelib
rm -rf %{buildroot}%{_libdir}/python%{python_version}/lib-tk

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files curses
%manifest %name.manifest
%defattr(644, root, root, 755)
%{_libdir}/python%{python_version}/curses
%{_libdir}/python%{python_version}/lib-dynload/_curses.so
%{_libdir}/python%{python_version}/lib-dynload/_curses_panel.so

%files
%manifest %name.manifest
%defattr(644, root, root, 755)
%dir %{_docdir}/%{name}
%doc %{_docdir}/%{name}/README
%doc %{_docdir}/%{name}/LICENSE
%config %{_sysconfdir}/pythonstart
%config %{_sysconfdir}/profile.d/python.*
%dir %{_libdir}/python%{python_version}
%{_libdir}/python%{python_version}/ssl.py*
%{_libdir}/python%{python_version}/bsddb
%{_libdir}/python%{python_version}/sqlite3
%dir %{_libdir}/python%{python_version}/lib-dynload
%{_libdir}/python%{python_version}/lib-dynload/_bsddb.so
%{_libdir}/python%{python_version}/lib-dynload/_hashlib.so
%{_libdir}/python%{python_version}/lib-dynload/_sqlite3.so
%{_libdir}/python%{python_version}/lib-dynload/_ssl.so
%{_libdir}/python%{python_version}/lib-dynload/readline.so

%changelog
