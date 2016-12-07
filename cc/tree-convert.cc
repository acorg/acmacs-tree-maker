#include <iostream>
#include <string>
#include <vector>
#include <stack>

#pragma GCC diagnostic push
#ifdef __clang__
#pragma GCC diagnostic ignored "-Wdeprecated"
#pragma GCC diagnostic ignored "-Wdisabled-macro-expansion"
#pragma GCC diagnostic ignored "-Wdocumentation"
#pragma GCC diagnostic ignored "-Wdocumentation-unknown-command"
#pragma GCC diagnostic ignored "-Wglobal-constructors"
#pragma GCC diagnostic ignored "-Wextra-semi"
#pragma GCC diagnostic ignored "-Wold-style-cast"
#pragma GCC diagnostic ignored "-Wreserved-id-macro"
#pragma GCC diagnostic ignored "-Wsign-conversion"
#pragma GCC diagnostic ignored "-Wshadow"
#pragma GCC diagnostic ignored "-Wundef"
#pragma GCC diagnostic ignored "-Wunused-parameter"
// #pragma GCC diagnostic ignored "-Wexit-time-destructors"
#endif

#include "boost/spirit/home/x3.hpp"
#include "boost/spirit/home/x3/support/ast/variant.hpp"
#include "boost/fusion/include/adapt_struct.hpp"

#pragma GCC diagnostic pop

// ----------------------------------------------------------------------

#pragma GCC diagnostic push
#ifdef __clang__
#pragma GCC diagnostic ignored "-Wdisabled-macro-expansion"
#pragma GCC diagnostic ignored "-Wglobal-constructors"
#pragma GCC diagnostic ignored "-Wunused-parameter"
#endif

namespace ast
{
    namespace x3 = boost::spirit::x3;
    struct Node;

    struct NodeElement : public x3::variant<std::string, std::vector<Node>>
    {
        using base_type::base_type;
        using base_type::operator=;
    };

    struct Node
    {
        NodeElement element;
        double length;
    };
}

BOOST_FUSION_ADAPT_STRUCT(
    ast::Node,
    (ast::NodeElement, element)
    (double, length)
)

namespace parser
{
    namespace x3 = boost::spirit::x3;
    using x3::ascii::char_;

    const auto label = x3::lexeme[+(char_ - char_(" \n:(),;"))];
    const auto branch_length = ':' >> x3::double_;

    x3::rule<class NodeElement, ast::NodeElement> const node_element = "node_element";
    x3::rule<class Node, ast::Node> const node = "node";
    x3::rule<class Tree, ast::Node> const tree = "tree";

    auto const node_element_def = label | ('(' >> (node % ',') >> ')');
    auto const node_def = node_element >> -branch_length;
    auto const tree_def = node >> ';';

    BOOST_SPIRIT_DEFINE(node_element, node, tree);
}

#pragma GCC diagnostic pop

// ----------------------------------------------------------------------

int main()
{
    ast::Node tree;
      // ast::Node node;

    std::cin.unsetf(std::ios::skipws);
    std::string input(std::istream_iterator<char>{std::cin}, std::istream_iterator<char>{});

    bool r = phrase_parse(input.begin(), input.end(), parser::tree, boost::spirit::x3::ascii::space, tree);
      // bool r = phrase_parse(input.begin(), input.end(), parser::node, boost::spirit::x3::ascii::space, node);

    if (r) {
        std::cout << "-------------------------\n";
        std::cout << "Parsing succeeded\n";
          // std::cout << "got: " << my_tree << std::endl;
        std::cout << "\n-------------------------\n";
    }
    else {
        std::cout << "-------------------------\n";
        std::cout << "Parsing failed\n";
        std::cout << "-------------------------\n";
    }

    std::cout << "Bye... :-) \n\n";
    return 0;
}

// ----------------------------------------------------------------------
/// Local Variables:
/// eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
/// End:
