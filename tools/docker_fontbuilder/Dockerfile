from debian/sortsmill

RUN  apt-get update && apt-get install -y\
	subversion \
	ant

# pdfoutline
# fntsample
# hb-shape
# ot-sanitise

RUN mkdir /var/build;

RUN cd /var/build \
 	&& svn checkout http://sfntly.googlecode.com/svn/trunk/ sfntly-read-only

RUN apt-get install -y libicu-dev openjdk-7-jdk

ENV JAVA_TOOL_OPTIONS -Dfile.encoding=UTF8

RUN cd	/var/build/sfntly-read-only/java \
	&& ant

RUN echo "#! /bin/sh" > /usr/local/bin/sfnttool \
        && echo "java -jar /var/build/sfntly-read-only/java/dist/tools/sfnttool/sfnttool.jar \$@" >> /usr/local/bin/sfnttool \
        && chmod +x /usr/local/bin/sfnttool

RUN cd /var/build \
	&& git clone https://github.com/google/woff2.git \
	&& cd woff2 \
	&& git submodule init \
	&& git submodule update \
	&& make clean all \
	&& ln -s `pwd`/woff2_compress /usr/local/bin/ \
	&& ln -s `pwd`/woff2_decompress /usr/local/bin/

RUN apt-get install -y python-numpy

RUN cd /var/build \
	&& git clone https://github.com/behdad/fonttools.git \
	&& cd fonttools \
	&& python setup.py install

RUN  cd /var/build \
	&& git clone --recursive https://github.com/khaledhosny/ots.git \
	&& cd ots \
	&& ./autogen.sh \
	&& ./configure \
	&&  make \
	&& ln -s `pwd`/out/Default/ot-sanitise /usr/local/bin

RUN apt-get install -y \
	gobject-introspection \
	python-gobject-dev \
	pkg-config ragel gtk-doc-tools \
	libgirepository1.0-dev

RUN cd /var/build \
	&& git clone https://github.com/behdad/harfbuzz.git

run cd var/build/harfbuzz \
	&& ./autogen.sh \
	&& make distclean \
	&& mkdir .build \
	&& cd .build \
	&&  ../configure --with-gobject --enable-introspection \
	&& make \
	&& make install

RUN apt-get install -y libpdf-api2-perl libintl-perl fntsample texlive-xetex wget xzdec latexmk

RUN tlmgr init-usertree \
	&& tlmgr install bidi iftex

RUN cd var/build \
	&& git clone https://github.com/robofab-developers/robofab.git \
	&& cd robofab \
	&& git checkout ufo3k \
	&& python install.py


# todo: precompile these:
# ;;; compiling /usr/local/share/guile/site/2.0/sortsmill/fonts/anchors.scm
# ;;; compiling /usr/local/share/guile/site/2.0/sortsmill/fonts/views.scm
# ;;; compiling /usr/local/share/guile/site/2.0/sortsmill/fontforge-api.scm
# ;;; compiled /root/.cache/guile/ccache/2.0-LE-8-2.0/usr/local/share/guile/site/2.0/sortsmill/fontforge-api.scm.go
#;;; compiled /root/.cache/guile/ccache/2.0-LE-8-2.0/usr/local/share/guile/site/2.0/sortsmill/fonts/views.scm.go
#;;; compiled /root/.cache/guile/ccache/2.0-LE-8-2.0/usr/local/share/guile/site/2.0/sortsmill/fonts/anchors.scm.go


# add fontforge to the mix
# fontforge is better in reading and writing ufo from sfd
# because these improvements came after the sortsmill fork, AFAIK.

RUN apt-get install -y \
	packaging-dev \
	pkg-config \
	python-dev \
	giflib-dbg \
	libjpeg-dev \
	libtiff-dev \
	uthash-dev \
	automake \
	flex \
	bison \
	&& rm -rf /var/lib/apt/lists/*

# build libuninameslist

RUN cd /var/build \
	&& git clone https://github.com/fontforge/libuninameslist.git \
	&& cd libuninameslist \
	&& autoreconf -i \
	&& automake --foreign \
	&& mkdir .build \
	&& cd .build \
	&& ../configure \
	&& make \
	&& make install

RUN cd /var/build \
	&& git clone https://github.com/fontforge/fontforge.git\
	&& cd fontforge \
	&& ./bootstrap \
	&& mkdir .build \
	&& cd .build \
	&& ../configure \
	&& make \
	&& make install \
	&& ldconfig
