#include "tree.hh"
#include "newick-parser.hh"
#include "export.hh"

// ----------------------------------------------------------------------

int main(int argc, const char* const* argv)
{
    int exit_code = 0;
    if (argc == 1) {
        std::cin.unsetf(std::ios::skipws);
        std::string input(std::istream_iterator<char>{std::cin}, std::istream_iterator<char>{});

        ast::Tree tree;
        try {
            import_newick(input, tree);
            std::cout << tree << std::endl;
        }
        catch (NewickImportFailed&) {
            exit_code = 1;
        }
    }
    else {
        std::cerr << "Usage: " << argv[0] << " <newick-tree.phy | xz -9e >tree.json\n";
        exit_code = 1;
    }
    return exit_code;
}

// ----------------------------------------------------------------------
/// Local Variables:
/// eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
/// End:
