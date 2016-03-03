.PHONY: all clean ttf web check release

FAMILY=Jomhuria
NAME=$(FAMILY)-Regular
SOURCENAME=jomhuria
VERSION=`cat VERSION.txt`

TOOLS=Tools
SRC=Sources
DDT=Sources/Documents
FONTDIR=Fonts
DIST=releases
WEB=$(FONTDIR)/webfonts
DOCS=Documents
DDTOUT=$(DOCS)/Testing
FONTS=$(NAME)

BUILD=$(TOOLS)/build.py
MAKECLR=$(TOOLS)/makeclr.py
MAKECSS=$(TOOLS)/makecss.py
MAKEWEB=$(TOOLS)/makeweb.py
PY=python2
FF=$(PY) $(BUILD)
SFNTTOOL=sfnttool
WOFF2_COMPRESS=woff2_compress
PP=gpp +c "/*" "*/" +c "//" "\n" +c "\\\n" "" -I$(SRC)

SFDS=$(FONTS:%=$(SRC)/%.sfdir)
DTTF=$(FONTS:%=$(FONTDIR)/%.ttf)
WTTF=$(FONTS:%=$(WEB)/%.ttf)
WOFF=$(FONTS:%=$(WEB)/%.woff)
WOF2=$(FONTS:%=$(WEB)/%.woff2)
EOTS=$(FONTS:%=$(WEB)/%.eot)
CSSS=$(WEB)/$(NAME).css
RELEASE=$(DIST)/$(FAMILY)-$(VERSION)
WRELEASE=$(DIST)/$(FAMILY)-$(VERSION)-webfonts

TEXS=$(wildcard $(DDT)/*.tex)
PDFTABLE=$(DDTOUT)/$(NAME)-table.pdf
DDTDOCS=$(TEXS:$(DDT)/%.tex=$(DDTOUT)/%.pdf)


FEAT=$(wildcard $(SRC)/*.fea)

license=OFL.txt OFL-FAQ.txt

all: ttf web

ttf: $(DTTF)
web: $(WTTF) $(WOFF) $(WOF2) $(EOTS) $(CSSS)
doc: $(PDFTABLE) $(DDTDOCS)
release: RELEASE

$(FONTDIR)/$(NAME).ttf: $(SRC)/$(SOURCENAME).sfdir $(SRC)/$(SOURCENAME)-latin.ufo $(SRC)/$(SOURCENAME).fea $(FEAT) $(BUILD)
	@echo "   FF	$@"
	@mkdir -p $(FONTDIR)
	@$(PP) $(SRC)/$(SOURCENAME).fea -o $(FONTDIR)/$(SOURCENAME).fea.pp
	@$(FF) --input $< --output $@ --latin $(SRC)/$(SOURCENAME)-latin.ufo --features=$(FONTDIR)/$(SOURCENAME).fea.pp --version $(VERSION)

$(WEB)/%.ttf: $(FONTDIR)/%.ttf $(MAKEWEB)
	@echo "   FF	$@"
	@mkdir -p $(WEB)
	@$(PY) $(MAKEWEB) $< $@ 1>/dev/null 2>&1

$(WEB)/%.woff: $(WEB)/%.ttf
	@echo "   FF	$@"
	@mkdir -p $(WEB)
	@$(SFNTTOOL) -w $< $@

$(WEB)/%.woff2: $(WEB)/%.ttf
	@echo "   FF	$@"
	@mkdir -p $(WEB)
	@$(WOFF2_COMPRESS) $< 1>/dev/null

$(WEB)/%.eot: $(WEB)/%.ttf
	@echo "   FF	$@"
	@mkdir -p $(WEB)
	@$(SFNTTOOL) -e -x $< $@

$(WEB)/%.css: $(WTTF) $(MAKECSS)
	@echo "   FONTDIR	$@"
	@mkdir -p $(WEB)
	@$(PY) $(MAKECSS) --css=$@ --fonts="$(WTTF)"

$(DDTOUT)/$(NAME)-table.pdf: $(FONTDIR)/$(NAME).ttf
	@echo "   FONTDIR	$@"
	@mkdir -p $(DDTOUT)
	@fntsample --font-file $< --output-file $@.tmp --print-outline > $@.txt
	@pdfoutline $@.tmp $@.txt $@
	@rm -f $@.tmp $@.txt

$(DDTOUT)/%.pdf: $(DDT)/%.tex $(FONTDIR)/$(NAME).ttf
	@echo "   FONTDIR	$< $@"
	@mkdir -p $(DDTOUT)
	@latexmk --norc --xelatex --quiet --output-directory=${DDTOUT} $<

$(RELEASE)/$(FAMILY)-$(VERSION):$(FONTDIR)/$(NAME).ttf FONTLOG README
	@echo "   FONTDIR	$@"

clean:
	rm -rfv $(DTTF) $(WTTF) $(WOFF) $(WOF2) $(EOTS) $(CSSS) $(PDFS) $(SRC)/$(NAME).fea.pp

dist: all
	@echo "   Making dist tarball"
	@mkdir -p $(RELEASE)
	@mkdir -p $(WRELEASE)
	@cp $(DDT)/RELEASE-README $(RELEASE)/README.txt
	@cp $(DDT)/RELEASE-README $(WRELEASE)/README.txt
	@cp OFL.txt $(RELEASE)
	@cp OFL.txt $(WRELEASE)
	@cp $(DTTF) $(RELEASE)
	@cp $(WEB)/* $(WRELEASE)
	@cd $(RELEASE) && zip -r $(basename `pwd`).zip .
	@cd $(WRELEASE) && zip -r $(basename `pwd`).zip .
