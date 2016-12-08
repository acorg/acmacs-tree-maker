# -*- Makefile -*-
# Eugene Skepner 2016
# ======================================================================

MAKEFLAGS = -w

# ----------------------------------------------------------------------

TREE_NEWICK_TO_JSON_SOURCES = tree-newick-to-json.cc
TREE_NEWICK_TO_JSON_PY_SOURCES = tree-newick-to-json-py.cc

# ----------------------------------------------------------------------

CLANG = $(shell if g++ --version 2>&1 | grep -i llvm >/dev/null; then echo Y; else echo N; fi)
ifeq ($(CLANG),Y)
  WEVERYTHING = -Weverything -Wno-c++98-compat -Wno-c++98-compat-pedantic -Wno-padded
  WARNINGS = -Wno-weak-vtables # -Wno-padded
  STD = c++14
else
  WEVERYTHING = -Wall -Wextra
  WARNINGS =
  STD = c++14
endif

# -fvisibility=hidden and -flto make resulting lib smaller (pybind11) but linking is much slower
OPTIMIZATION = -O3 #-fvisibility=hidden -flto
PROFILE = # -pg
CXXFLAGS = -MMD -g $(OPTIMIZATION) $(PROFILE) -fPIC -std=$(STD) $(WEVERYTHING) $(WARNINGS) -Icc -I$(BUILD)/include -I$(ACMACSD_ROOT)/include $(PKG_INCLUDES)
LDFLAGS = $(OPTIMIZATION) $(PROFILE)

PYTHON_VERSION = $(shell python3 -c 'import sys; print("{0.major}.{0.minor}".format(sys.version_info))')
PYTHON_CONFIG = python$(PYTHON_VERSION)-config
PYTHON_MODULE_SUFFIX = $(shell $(PYTHON_CONFIG) --extension-suffix)
PYTHON_LD_LIB = $$($(PYTHON_CONFIG) --ldflags | sed -E 's/-Wl,-stack_size,[0-9]+//')

PKG_INCLUDES = $$($(PYTHON_CONFIG) --includes)

# ----------------------------------------------------------------------

BUILD = build
DIST = $(abspath dist)

# ----------------------------------------------------------------------

all: check-python $(DIST)/tree-newick-to-json $(DIST)/tree_newick_to_json$(PYTHON_MODULE_SUFFIX)

install: install-tree-maker

# ----------------------------------------------------------------------

$(DIST)/tree-newick-to-json: $(patsubst %.cc,$(BUILD)/%.o,$(TREE_NEWICK_TO_JSON_SOURCES)) | $(DIST) check-acmacsd-root
	g++ $(LDFLAGS) -o $@ $^

$(DIST)/tree_newick_to_json$(PYTHON_MODULE_SUFFIX):  $(patsubst %.cc,$(BUILD)/%.o,$(TREE_NEWICK_TO_JSON_PY_SOURCES)) | $(DIST) check-acmacsd-root
	g++ -shared $(LDFLAGS) -o $@ $^ $(PYTHON_LD_LIB)

# ----------------------------------------------------------------------

install-tree-maker: $(DIST)/tree-newick-to-json $(DIST)/tree_newick_to_json$(PYTHON_MODULE_SUFFIX) | check-acmacsd-root
	ln -sf $(abspath bin)/tree-* $(ACMACSD_ROOT)/bin
	ln -sf $(abspath py)/* $(ACMACSD_ROOT)/py
	ln -sf $(DIST)/tree-* $(ACMACSD_ROOT)/bin
	ln -sf $(DIST)/tree_newick_to_json$(PYTHON_MODULE_SUFFIX) $(ACMACSD_ROOT)/py

clean:
	rm -rf $(DIST) $(BUILD)/*.o $(BUILD)/*.d

distclean: clean
	rm -rf $(BUILD)

# ----------------------------------------------------------------------

$(BUILD)/%.o: cc/%.cc | $(BUILD)
	@echo $<
	@g++ $(CXXFLAGS) -c -o $@ $<

# ----------------------------------------------------------------------

check-acmacsd-root:
ifndef ACMACSD_ROOT
	$(error ACMACSD_ROOT is not set)
endif

check-python:
	@printf 'import sys\nif sys.version_info < (3, 5):\n print("Python 3.5 is required")\n exit(1)' | python3

$(DIST):
	mkdir -p $(DIST)

$(BUILD):
	mkdir -p $(BUILD)

.PHONY: check-acmacsd-root check-python

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
