SOURCES:=unin.erl temp.erl

SRCDIR:=src
EBINDIR=ebin
EBINS:=$(patsubst %.erl,$(EBINDIR)/%.beam,$(SOURCES))

ERLC=erlc

all: $(EBINDIR) $(EBINS)

clean:
	rm -rf $(EBINDIR)

$(EBINDIR):
	mkdir $(EBINDIR)

$(EBINS): $(EBINDIR)/%.beam: $(SRCDIR)/%.erl
	$(ERLC) -o $(EBINDIR) $<
