# -*- Makefile -*-
# Eugene Skepner 2016
# ======================================================================

all: check-python install

install: check-acmacsd-root install-tree-maker

# ----------------------------------------------------------------------

install-tree-maker:
	ln -sf $(abspath bin)/tree-* $(ACMACSD_ROOT)/bin

# ----------------------------------------------------------------------

check-acmacsd-root:
ifndef ACMACSD_ROOT
	$(error ACMACSD_ROOT is not set)
endif

check-python:
	@printf 'import sys\nif sys.version_info < (3, 5):\n print("Python 3.5 is required")\n exit(1)' | python3

.PHONY: check-acmacsd-root check-python

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
