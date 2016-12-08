#include "tree.hh"
#include "newick-parser.hh"
#include "export.hh"
#include "acmacs-base/pybind11.hh"

// ----------------------------------------------------------------------

PYBIND11_PLUGIN(tree_newick_to_json)
{
    py::module m("tree_newick_to_json", "Importing newick tree plugin");

    py::class_<ast::Tree>(m, "Tree")
            .def(py::init<>())
            ;

    m.def("import_newick", &import_newick, py::arg("input"), py::arg("tree"));
    m.def("json", &tree_to_json, py::arg("tree"));

    return m.ptr();
}

// ----------------------------------------------------------------------
/// Local Variables:
/// eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
/// End:
