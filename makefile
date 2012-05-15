RM = rm -f
ECHO = echo
MAKE = make
PYTHON = python

help:
	@$(ECHO) "init  the app. plz make init"
	@$(ECHO) "clean the app. plz make clean"

.PHONY:init init_db clean clean_all

init:
	$(MAKE) clean_all
	$(ECHO) "Init The App"
	$(PYTHON) init.py

init_db:
	$(RM) .messages
	sqlite3 .messages<db_file.sql

clean:
	$(RM) *.pyc

clean_all:
	$(RM) .messages
	$(RM) .gsid
	$(RM) .tokens
