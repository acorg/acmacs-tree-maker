# -*- Makefile -*-
# Eugene Skepner 2016
# ======================================================================

MAKEFLAGS = -w

# ----------------------------------------------------------------------

TREE_NEWICK_TO_JSON_SOURCES = tree-newick-to-json.cc
TREE_NEWICK_TO_JSON_PY_SOURCES = tree-newick-to-json-py.cc

# ----------------------------------------------------------------------

TARGET_ROOT=$(shell if [ -f /Volumes/rdisk/ramdisk-id ]; then echo /Volumes/rdisk/AD; else echo $(ACMACSD_ROOT); fi)
include $(TARGET_ROOT)/share/Makefile.g++
include $(TARGET_ROOT)/share/Makefile.dist-build.vars

# -fvisibility=hidden and -flto make resulting lib smaller (pybind11) but linking is much slower
OPTIMIZATION = -O3 #-fvisibility=hidden -flto
PROFILE = # -pg
CXXFLAGS = -MMD -g $(OPTIMIZATION) $(PROFILE) -fPIC -std=$(STD) $(WEVERYTHING) $(WARNINGS) -Icc -I$(AD_INCLUDE) $(PKG_INCLUDES)
LDFLAGS = $(OPTIMIZATION) $(PROFILE)

PYTHON_VERSION = $(shell python3 -c 'import sys; print("{0.major}.{0.minor}".format(sys.version_info))')
PYTHON_CONFIG = python$(PYTHON_VERSION)-config
PYTHON_MODULE_SUFFIX = $(shell $(PYTHON_CONFIG) --extension-suffix)
PYTHON_LD_LIB = $(shell pkg-config --libs liblzma) $(shell $(PYTHON_CONFIG) --ldflags | sed -E 's/-Wl,-stack_size,[0-9]+//')
LD_LIBS = -L$(AD_LIB) -lacmacsbase -lboost_filesystem -lboost_system
PKG_INCLUDES = $(shell pkg-config --cflags liblzma) $(shell $(PYTHON_CONFIG) --includes)

# ----------------------------------------------------------------------

all: check-python $(DIST)/tree-newick-to-json $(DIST)/tree_newick_to_json$(PYTHON_MODULE_SUFFIX)

install: install-tree-maker

test: test-newick-to-json

# ----------------------------------------------------------------------

$(DIST)/tree-newick-to-json: $(patsubst %.cc,$(BUILD)/%.o,$(TREE_NEWICK_TO_JSON_SOURCES)) | $(DIST) check-acmacsd-root
	$(CXX) $(LDFLAGS) -o $@ $^ $(LD_LIBS)

$(DIST)/tree_newick_to_json$(PYTHON_MODULE_SUFFIX):  $(patsubst %.cc,$(BUILD)/%.o,$(TREE_NEWICK_TO_JSON_PY_SOURCES)) | $(DIST) check-acmacsd-root
	$(CXX) -shared $(LDFLAGS) -o $@ $^ $(LD_LIBS) $(PYTHON_LD_LIB)

# ----------------------------------------------------------------------

install-tree-maker: $(DIST)/tree-newick-to-json $(DIST)/tree_newick_to_json$(PYTHON_MODULE_SUFFIX) | check-acmacsd-root
	ln -sf $(abspath bin)/tree-* $(AD_BIN)
	ln -sf $(abspath py)/* $(AD_PY)
	ln -sf $(DIST)/tree-* $(AD_BIN)
	ln -sf $(DIST)/tree_newick_to_json$(PYTHON_MODULE_SUFFIX) $(AD_PY)

test-newick-to-json: $(DIST)/tree-newick-to-json
	env LD_LIBRARY_PATH=$(AD_LIB) $(DIST)/tree-newick-to-json <test/newick.phy | diff test/newick.json -

-include $(BUILD)/*.d

include $(AD_SHARE)/Makefile.rtags

# ----------------------------------------------------------------------

$(BUILD)/%.o: cc/%.cc | $(BUILD)
	@echo $<
	@$(CXX) $(CXXFLAGS) -c -o $@ $<

# ----------------------------------------------------------------------

include $(AD_SHARE)/Makefile.dist-build.rules

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
