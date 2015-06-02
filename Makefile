.PHONY: all clean ttf web pack check

NAME=Jomhuria-Regular
SOURCENAME=jomhuria
VERSION=0.001

TOOLS=tools
SRC=sources
DDT=document-sources
GEN=generated
WEB=$(GEN)/webfonts
DDTOUT=$(GEN)/documents
TESTS=test-suite
FONTS=$(NAME)
DIST=$(NAME)-$(VERSION)
DOCS=README README-Arabic NEWS NEWS-Arabic
DIST=$(NAME)-$(VERSION)



BUILD=$(TOOLS)/build.py
RUNTEST=$(TOOLS)/runtest.py
MAKECLR=$(TOOLS)/makeclr.py
MAKECSS=$(TOOLS)/makecss.py
MAKEWEB=$(TOOLS)/makeweb.py
PY=python
FF=$(PY) $(BUILD)
SFNTTOOL=sfnttool
WOFF2_COMPRESS=woff2_compress
PP=gpp +c "/*" "*/" +c "//" "\n" +c "\\\n" "" -I$(SRC)

SFDS=$(FONTS:%=$(SRC)/%.sfdir)
DTTF=$(FONTS:%=$(GEN)/%.ttf)
WTTF=$(FONTS:%=$(WEB)/%.ttf)
WOFF=$(FONTS:%=$(WEB)/%.woff)
WOF2=$(FONTS:%=$(WEB)/%.woff2)
EOTS=$(FONTS:%=$(WEB)/%.eot)
CSSS=$(WEB)/$(NAME).css

TEXS=$(wildcard $(DDT)/*.tex)
PDFTABLE=$(DDTOUT)/$(NAME)-table.pdf
DDTDOCS=$(TEXS:$(DDT)/%.tex=$(DDTOUT)/%.pdf)


FEAT=$(wildcard $(SRC)/*.fea)
TEST=$(wildcard $(TESTS)/*.test)
TEST+=$(wildcard $(TESTS)/*.ptest)

license=OFL.txt OFL-FAQ.txt

all: ttf web

ttf: $(DTTF)
web: $(WTTF) $(WOFF) $(WOF2) $(EOTS) $(CSSS)
doc: $(PDFTABLE) $(DDTDOCS)

$(GEN)/$(NAME).ttf: $(SRC)/$(SOURCENAME).sfdir $(SRC)/$(SOURCENAME)-latin.sfdir $(SRC)/$(SOURCENAME).fea $(FEAT) $(BUILD)
	@echo "   FF	$@"
	@mkdir -p $(GEN)
	@$(PP) $(SRC)/$(SOURCENAME).fea -o $(SRC)/$(SOURCENAME).fea.pp
	@$(FF) --input $< --output $@ --latin $(SRC)/$(SOURCENAME)-latin.sfdir --features=$(SRC)/$(SOURCENAME).fea.pp --version $(VERSION)

$(WEB)/%.ttf: $(GEN)/%.ttf $(MAKEWEB)
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
	@echo "   GEN	$@"
	@mkdir -p $(WEB)
	@$(PY) $(MAKECSS) --css=$@ --fonts="$(WTTF)"

$(DDTOUT)/$(NAME)-table.pdf: $(GEN)/$(NAME).ttf
	@echo "   GEN	$@"
	@mkdir -p $(DDTOUT)
	@fntsample --font-file $< --output-file $@.tmp --print-outline > $@.txt
	@pdfoutline $@.tmp $@.txt $@
	@rm -f $@.tmp $@.txt

$(DDTOUT)/%.pdf: $(DDT)/%.tex $(GEN)/$(NAME).ttf
	@echo "   GEN	$< $@"
	@mkdir -p $(DDTOUT)
	@latexmk --norc --xelatex --quiet --output-directory=${DDTOUT} $<

check: $(TEST) $(DTTF)
	@echo "running tests"
	@$(foreach font,$(DTTF),echo "OTS\t$(font)" && ot-sanitise $(font) &&) true
	@$(PY) $(RUNTEST) $(TEST)

clean:
	rm -rfv $(DTTF) $(WTTF) $(WOFF) $(WOF2) $(EOTS) $(CSSS) $(PDFS) $(SRC)/$(NAME).fea.pp
