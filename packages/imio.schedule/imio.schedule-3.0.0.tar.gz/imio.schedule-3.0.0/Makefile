#!/usr/bin/make
#

options =

.PHONY: test instance cleanall

all: test

bin/python:
	virtualenv-2.7 .

develop-eggs: bin/python bootstrap.py
	./bin/python bootstrap.py

bin/sphinx-build: .installed.cfg
	@touch $@

bin/buildout: develop-eggs

bin/test: versions.cfg buildout.cfg bin/buildout setup.py
	./bin/buildout -t 5
	touch $@

bin/instance: versions.cfg buildout.cfg bin/buildout setup.py
	./bin/buildout -t 5 install instance
	touch $@

bin/templates: setup.py buildout.cfg
	./bin/buildout -t 5 install templates
	touch $@

test: bin/test
	bin/test -s imio.schedule $(options)

instance: bin/instance
	bin/instance fg

cleanall:
	rm -fr bin develop-eggs downloads eggs parts .installed.cfg devel
