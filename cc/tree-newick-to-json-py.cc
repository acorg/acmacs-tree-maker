#include "tree.hh"
#include "newick-parser.hh"
#include "export.hh"
#include "acmacs-base/pybind11.hh"

// ----------------------------------------------------------------------

PYBIND11_MODULE(tree_newick_to_json, m)
{
    m.doc() = "Importing newick tree plugin";

    py::class_<ast::Tree>(m, "Tree")
            .def(py::init<>())
            ;

    m.def("import_newick", &import_newick, py::arg("input"), py::arg("tree"));
    m.def("json", &tree_to_json, py::arg("tree"));
}

// ----------------------------------------------------------------------
/// Local Variables:
/// eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
/// End:
