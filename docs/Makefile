#
#	Build usable docs
#

ASCIIDOCTOR = asciidoctor
PANDOC = pandoc
DOCS = reqts.adoc
MD = $(DOCS:.adoc=.md)
HTML = $(DOCS:.adoc=.html)
PDF = $(DOCS:.adoc=.pdf)
XML = $(DOCS:.adoc=.xml)

# Build the platform spec in several formats
all: $(MD) $(HTML) $(PDF)
	touch $@

clean:
	rm -f $(MD) $(XML) $(HTML) $(PDF)

# handy shortcuts for installing necessary packages: YMMV
install-debs:
	sudo apt-get install pandoc asciidoctor ruby-asciidoctor-pdf

install-rpms:
	sudo dnf install pandoc rubygem-asciidoctor rubygem-asciidoctor-pdf

%.md : %.xml
	$(PANDOC) -f docbook -t markdown_strict $< -o $@ 

%.xml: %.adoc
	$(ASCIIDOCTOR) -d book -b docbook $<

%.pdf: %.adoc
	$(ASCIIDOCTOR) -d book -r asciidoctor-pdf -b pdf $<

%.html: %.adoc
	$(ASCIIDOCTOR) -d book -b html $<

