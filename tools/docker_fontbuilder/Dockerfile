from debian/sortsmill

RUN  apt-get update && apt-get install -y\
	subversion \
	ant \
	libicu-dev \
	openjdk-7-jdk \
	python-numpy \
	gobject-introspection \
	python-gobject-dev \
	pkg-config ragel gtk-doc-tools \
	libgirepository1.0-dev \
	libpdf-api2-perl \
	libintl-perl \
	fntsample \
	texlive-xetex \
	wget \
	xzdec \
	latexmk \
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

# pdfoutline
# fntsample
# hb-shape
# ot-sanitise

RUN mkdir -p /var/build;

RUN cd /var/build \
 	&& svn checkout http://sfntly.googlecode.com/svn/trunk/ sfntly-read-only

ENV JAVA_TOOL_OPTIONS -Dfile.encoding=UTF8

RUN cd	/var/build/sfntly-read-only/java \
	&& ant

RUN echo "#! /bin/sh" > /usr/local/bin/sfnttool \
        && echo "java -jar /var/build/sfntly-read-only/java/dist/tools/sfnttool/sfnttool.jar \$@" >> /usr/local/bin/sfnttool \
        && chmod +x /usr/local/bin/sfnttool

RUN cd /var/build \
	&& git clone https://github.com/google/woff2.git \
	&& cd woff2 \
	&& echo `git config --get remote.origin.url` at `git rev-parse HEAD` >> /var/build/versions.txt \
	&& git submodule init \
	&& git submodule update \
	&& make clean all \
	&& ln -s `pwd`/woff2_compress /usr/local/bin/ \
	&& ln -s `pwd`/woff2_decompress /usr/local/bin/

RUN cd /var/build \
	&& git clone https://github.com/behdad/fonttools.git \
	&& cd fonttools \
	&& echo `git config --get remote.origin.url` at `git rev-parse HEAD` >> /var/build/versions.txt \
	&& python setup.py install \
	&& cd /var/build \
	&& rm -rf fonttools

RUN  cd /var/build \
	&& git clone --recursive https://github.com/khaledhosny/ots.git \
	&& cd ots \
	&& echo `git config --get remote.origin.url` at `git rev-parse HEAD` >> /var/build/versions.txt \
	&& ./autogen.sh \
	&& ./configure \
	&&  make \
	&& ln -s `pwd`/out/Default/ot-sanitise /usr/local/bin

RUN cd /var/build \
	&& git clone https://github.com/behdad/harfbuzz.git \
	&& cd harfbuzz \
	&& echo `git config --get remote.origin.url` at `git rev-parse HEAD` >> /var/build/versions.txt \
	&& ./autogen.sh \
	&& make distclean \
	&& mkdir .build \
	&& cd .build \
	&&  ../configure --with-gobject --enable-introspection \
	&& make \
	&& make install \
	&& cd /var/build \
	&& rm -rf harfbuzz

RUN tlmgr init-usertree \
	&& tlmgr install bidi iftex

RUN cd /var/build \
	&& git clone https://github.com/robofab-developers/robofab.git \
	&& cd robofab \
	&& echo `git config --get remote.origin.url` at `git rev-parse HEAD` >> /var/build/versions.txt \
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


# build libuninameslist

RUN cd /var/build \
	&& git clone https://github.com/fontforge/libuninameslist.git \
	&& cd libuninameslist \
	&& echo `git config --get remote.origin.url` at `git rev-parse HEAD` >> /var/build/versions.txt \
	&& autoreconf -i \
	&& automake --foreign \
	&& mkdir .build \
	&& cd .build \
	&& ../configure \
	&& make \
	&& make install \
	&& cd /var/build \
	&& rm -rf libuninameslist

RUN cd /var/build \
	&& git clone https://github.com/fontforge/fontforge.git\
	&& cd fontforge \
	&& echo `git config --get remote.origin.url` at `git rev-parse HEAD` >> /var/build/versions.txt \
	&& ./bootstrap \
	&& mkdir .build \
	&& cd .build \
	&& ../configure \
	&& make \
	&& make install \
	&& ldconfig \
	&& cd /var/build \
	&& rm -rf fontforge

RUN cd /var/build \
	&& git clone https://github.com/typesupply/defcon.git \
	&& cd defcon \
	&& echo `git config --get remote.origin.url` at `git rev-parse HEAD` >> /var/build/versions.txt \
	&& git checkout ufo3 \
	&& python setup.py install \
	&& cd /var/build \
	&& rm -rf defcon

RUN cd /var/build \
	&& git clone https://github.com/typemytype/booleanOperations.git \
	&& cd booleanOperations/cppWrapper \
	&& python setup.py build_ext --inplace \
	&& cp pyClipper.so ../Lib/booleanOperations/pyClipper.so \
	&& cd .. \
	&& echo `git config --get remote.origin.url` at `git rev-parse HEAD` >> /var/build/versions.txt \
	&& python setup.py install \
	&& cd /var/build \
	&& rm -rf booleanOperations
