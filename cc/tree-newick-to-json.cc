#include "tree.hh"
#include "newick-parser.hh"
#include "export.hh"

// ----------------------------------------------------------------------

int main()
{
    std::cin.unsetf(std::ios::skipws);
    std::string input(std::istream_iterator<char>{std::cin}, std::istream_iterator<char>{});

    ast::Tree tree;
    int exit_code = 0;
    try {
        import_newick(input, tree);
        std::cout << tree << std::endl;
    }
    catch (NewickImportFailed&) {
        exit_code = 1;
    }
    return exit_code;
}

// ----------------------------------------------------------------------
/// Local Variables:
/// eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
/// End:
