RM = rm -f
ECHO = echo
MAKE = make
PYTHON = python

help:
	@$(ECHO) "init  the app. plz make init"
	@$(ECHO) "clean the app. plz make clean"

.PHONY:init clean clean_all

init:
	$(MAKE) clean
	$(ECHO) "Init The App"
	$(PYTHON) init.py

clean:
	$(RM) *.pyc

clean_all:
	$(RM) .messages
	$(RM) .gsid
	$(RM) .tokens
