# -*- Makefile -*-
# Eugene Skepner 2017
# ======================================================================

MAKEFLAGS = -w

# ----------------------------------------------------------------------

TARGETS = \
	$(DIST)/tree-newick-to-json \
	$(TREE_NEWICK_TO_JSON_PY_LIB)

TREE_NEWICK_TO_JSON_PY_SOURCES = tree-newick-to-json-py.cc

TREE_NEWICK_TO_JSON_PY_LIB_MAJOR = 1
TREE_NEWICK_TO_JSON_PY_LIB_MINOR = 0
TREE_NEWICK_TO_JSON_PY_LIB_NAME = tree_newick_to_json
TREE_NEWICK_TO_JSON_PY_LIB = $(DIST)/$(TREE_NEWICK_TO_JSON_PY_LIB_NAME)$(PYTHON_MODULE_SUFFIX)

# ----------------------------------------------------------------------

include $(ACMACSD_ROOT)/share/makefiles/Makefile.g++
include $(ACMACSD_ROOT)/share/makefiles/Makefile.python
include $(ACMACSD_ROOT)/share/makefiles/Makefile.dist-build.vars

CXXFLAGS = -MMD -g $(OPTIMIZATION) $(PROFILE) -fPIC -std=$(STD) $(WARNINGS) -Icc -I$(AD_INCLUDE) $(PKG_INCLUDES)
LDFLAGS = $(OPTIMIZATION) $(PROFILE)

LDLIBS = $(AD_LIB)/$(call shared_lib_name,libacmacsbase,1,0)
PKG_INCLUDES = $(shell pkg-config --cflags liblzma) $(PYTHON_INCLUDES)

# ----------------------------------------------------------------------

all:  $(TARGETS)

install: $(TARGETS)
	$(call install_py_lib,$(TREE_NEWICK_TO_JSON_PY_LIB))
	ln -sf $(abspath bin)/tree-* $(AD_BIN)
	ln -sf $(abspath py)/* $(AD_PY)
	ln -sf $(DIST)/tree-* $(AD_BIN)

test: $(TARGETS)
	if [ "$$(uname)" == "Darwin" ]; then $(DIST)/tree-newick-to-json <test/newick.phy | diff test/newick.json -; fi

# ----------------------------------------------------------------------

-include $(BUILD)/*.d
include $(ACMACSD_ROOT)/share/makefiles/Makefile.dist-build.rules
include $(ACMACSD_ROOT)/share/makefiles/Makefile.rtags

# ----------------------------------------------------------------------

$(DIST)/%: $(BUILD)/%.o
	@printf "%-16s %s\n" "LINK" $@
	@$(CXX) $(LDFLAGS) -o $@ $^ $(LDLIBS) $(AD_RPATH)

$(TREE_NEWICK_TO_JSON_PY_LIB): $(patsubst %.cc,$(BUILD)/%.o,$(TREE_NEWICK_TO_JSON_PY_SOURCES)) | $(DIST)
	@printf "%-16s %s\n" "SHARED" $@
	@$(call make_shared,$(TREE_NEWICK_TO_JSON_PY_LIB_NAME),$(TREE_NEWICK_TO_JSON_PY_LIB_MAJOR),$(TREE_NEWICK_TO_JSON_PY_LIB_MINOR)) $(LDFLAGS) -o $@ $^ $(LDLIBS) $(PYTHON_LDLIBS)

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
