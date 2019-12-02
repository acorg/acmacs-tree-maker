# -*- Makefile -*-
# ======================================================================

TARGETS = \
	$(DIST)/tree-newick-to-json \
	$(TREE_NEWICK_TO_JSON_PY_LIB)

TREE_NEWICK_TO_JSON_PY_SOURCES = tree-newick-to-json-py.cc

TREE_NEWICK_TO_JSON_PY_LIB_MAJOR = 1
TREE_NEWICK_TO_JSON_PY_LIB_MINOR = 0
TREE_NEWICK_TO_JSON_PY_LIB_NAME = tree_newick_to_json
TREE_NEWICK_TO_JSON_PY_LIB = $(DIST)/$(TREE_NEWICK_TO_JSON_PY_LIB_NAME)$(PYTHON_MODULE_SUFFIX)

# ----------------------------------------------------------------------

all: install

CONFIGURE_PYTHON = 1
include $(ACMACSD_ROOT)/share/Makefile.config

LDLIBS = \
  $(AD_LIB)/$(call shared_lib_name,libacmacsbase,1,0) \
  $(CXX_LIBS)

# ----------------------------------------------------------------------

install: $(TARGETS)
	$(call install_py_lib,$(TREE_NEWICK_TO_JSON_PY_LIB))
	$(call symbolic_link_wildcard,$(abspath bin)/tree-*,$(AD_BIN))
	$(call symbolic_link,$(abspath bin)/make-trees,$(AD_BIN))
	$(call symbolic_link,$(abspath bin)/garli-score,$(AD_BIN))
	$(call symbolic_link_wildcard,$(abspath py)/*,$(AD_PY))
	$(call symbolic_link_wildcard,$(DIST)/tree-*,$(AD_BIN))

test: install
	if [ "$$(uname)" == "Darwin" ]; then $(DIST)/tree-newick-to-json <test/newick.phy | diff test/newick.json -; else echo WARNING: no tree-maker test run on $$(uname); fi
.PHONY: test

# ----------------------------------------------------------------------

$(DIST)/%: $(BUILD)/%.o
	$(call echo_link_exe,$@)
	$(CXX) $(LDFLAGS) -o $@ $^ $(LDLIBS) $(AD_RPATH)

$(TREE_NEWICK_TO_JSON_PY_LIB): $(patsubst %.cc,$(BUILD)/%.o,$(TREE_NEWICK_TO_JSON_PY_SOURCES)) | $(DIST)
	$(call echo_shared_lib,$@)
	$(call make_shared_lib,$(TREE_NEWICK_TO_JSON_PY_LIB_NAME),$(TREE_NEWICK_TO_JSON_PY_LIB_MAJOR),$(TREE_NEWICK_TO_JSON_PY_LIB_MINOR)) $(LDFLAGS) -o $@ $^ $(LDLIBS) $(PYTHON_LIBS)

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
