# -*- Makefile -*-
# Eugene Skepner 2017
# ======================================================================

MAKEFLAGS = -w

# ----------------------------------------------------------------------

TREE_NEWICK_TO_JSON_SOURCES = tree-newick-to-json.cc
TREE_NEWICK_TO_JSON_PY_SOURCES = tree-newick-to-json-py.cc

# ----------------------------------------------------------------------

include $(ACMACSD_ROOT)/share/makefiles/Makefile.g++
include $(ACMACSD_ROOT)/share/makefiles/Makefile.dist-build.vars

CXXFLAGS = -MMD -g $(OPTIMIZATION) $(PROFILE) -fPIC -std=$(STD) $(WARNINGS) -Icc -I$(AD_INCLUDE) $(PKG_INCLUDES)
LDFLAGS = $(OPTIMIZATION) $(PROFILE)

PYTHON_VERSION = $(shell python3 -c 'import sys; print("{0.major}.{0.minor}".format(sys.version_info))')
PYTHON_CONFIG = python$(PYTHON_VERSION)-config
PYTHON_MODULE_SUFFIX = $(shell $(PYTHON_CONFIG) --extension-suffix)
PYTHON_LD_LIB = $(shell pkg-config --libs liblzma) $(shell $(PYTHON_CONFIG) --ldflags | sed -E 's/-Wl,-stack_size,[0-9]+//')
LD_LIBS = -L$(AD_LIB) -lacmacsbase -lboost_filesystem -lboost_system
PKG_INCLUDES = $(shell pkg-config --cflags liblzma) $(shell $(PYTHON_CONFIG) --includes)

# ----------------------------------------------------------------------

all: $(DIST)/tree-newick-to-json $(DIST)/tree_newick_to_json$(PYTHON_MODULE_SUFFIX)

install: install-tree-maker

test: test-newick-to-json

# ----------------------------------------------------------------------

$(DIST)/tree-newick-to-json: $(patsubst %.cc,$(BUILD)/%.o,$(TREE_NEWICK_TO_JSON_SOURCES)) | $(DIST)
	@echo "LINK       " $@ # '<--' $^
	$(CXX) $(LDFLAGS) -o $@ $^ $(LD_LIBS)

$(DIST)/tree_newick_to_json$(PYTHON_MODULE_SUFFIX): $(patsubst %.cc,$(BUILD)/%.o,$(TREE_NEWICK_TO_JSON_PY_SOURCES)) | $(DIST)
	@echo "SHARED     " $@ # '<--' $^
	$(CXX) -shared $(LDFLAGS) -o $@ $^ $(LD_LIBS) $(PYTHON_LD_LIB)

install-headers:

# ----------------------------------------------------------------------

-include $(BUILD)/*.d
include $(ACMACSD_ROOT)/share/makefiles/Makefile.dist-build.rules
include $(ACMACSD_ROOT)/share/makefiles/Makefile.rtags

# ----------------------------------------------------------------------

install-tree-maker: $(DIST)/tree-newick-to-json $(DIST)/tree_newick_to_json$(PYTHON_MODULE_SUFFIX) | check-acmacsd-root
	ln -sf $(abspath bin)/tree-* $(AD_BIN)
	ln -sf $(abspath py)/* $(AD_PY)
	ln -sf $(DIST)/tree-* $(AD_BIN)
	ln -sf $(DIST)/tree_newick_to_json$(PYTHON_MODULE_SUFFIX) $(AD_PY)

test-newick-to-json: $(DIST)/tree-newick-to-json
	env LD_LIBRARY_PATH=$(AD_LIB) $(DIST)/tree-newick-to-json <test/newick.phy | diff test/newick.json -

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
