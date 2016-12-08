#include "tree.hh"
#include "newick-parser.hh"
#include "export.hh"

// ----------------------------------------------------------------------

int main()
{
    namespace x3 = boost::spirit::x3;
    ast::Tree tree;

    std::cin.unsetf(std::ios::skipws);
    std::string input(std::istream_iterator<char>{std::cin}, std::istream_iterator<char>{});

    auto iter = input.begin();
    parser::error_handler<std::string::const_iterator> error_handler{iter, input.end(), std::cerr}; //, "input"};

    auto const pp = x3::with<parser::error_handler_tag>(std::ref(error_handler))[parser::tree];

    bool success = phrase_parse(iter, input.end(), pp, boost::spirit::x3::ascii::space, tree);

    int exit_code = 1;
    if (success) {
        if (iter != input.end()) {
            error_handler(iter, "ERROR: expecting end of input here: ");
        }
        else {
            std::cout << tree << std::endl;
            exit_code = 0;
        }
    }

    return exit_code;
}

// ----------------------------------------------------------------------
/// Local Variables:
/// eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
/// End:
