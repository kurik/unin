SOURCES:=unin.erl temp.erl

SRCDIR:=src
EBINDIR=ebin
EBINS:=$(patsubst %.erl,$(EBINDIR)/%.beam,$(SOURCES))

ERLC=erlc

all: $(EBINS)

clean:
	rm -rf $(EBINDIR)/*

$(EBINS): $(EBINDIR)/%.beam: $(SRCDIR)/%.erl
	$(ERLC) -o $(EBINDIR) $<
