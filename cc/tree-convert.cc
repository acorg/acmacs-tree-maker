#include <iostream>
#include <string>
#include <vector>
#include <map>

#pragma GCC diagnostic push
#ifdef __clang__
#pragma GCC diagnostic ignored "-Wdeprecated"
#pragma GCC diagnostic ignored "-Wdisabled-macro-expansion"
#pragma GCC diagnostic ignored "-Wdocumentation"
#pragma GCC diagnostic ignored "-Wdocumentation-unknown-command"
#pragma GCC diagnostic ignored "-Wglobal-constructors"
#pragma GCC diagnostic ignored "-Wextra-semi"
#pragma GCC diagnostic ignored "-Wimplicit-fallthrough"
#pragma GCC diagnostic ignored "-Wold-style-cast"
#pragma GCC diagnostic ignored "-Wreserved-id-macro"
#pragma GCC diagnostic ignored "-Wsign-conversion"
#pragma GCC diagnostic ignored "-Wshadow"
#pragma GCC diagnostic ignored "-Wundef"
#pragma GCC diagnostic ignored "-Wunused-parameter"
// #pragma GCC diagnostic ignored "-Wexit-time-destructors"
#endif

#define BOOST_SPIRIT_X3_NO_FILESYSTEM 1

#include "boost/spirit/home/x3.hpp"
#include "boost/spirit/home/x3/support/ast/variant.hpp"
#include "boost/spirit/home/x3/support/ast/position_tagged.hpp"
#include "boost/spirit/home/x3/support/utility/error_reporting.hpp"
#include <boost/spirit/home/x3/support/utility/annotate_on_success.hpp>
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

    struct Tree : public Node
    {
    };
}

BOOST_FUSION_ADAPT_STRUCT(
    ast::Node,
    (ast::NodeElement, element)
    (double, length)
)

BOOST_FUSION_ADAPT_STRUCT(
    ast::Tree,
    (ast::NodeElement, element)
    (double, length)
)

namespace parser
{
    namespace x3 = boost::spirit::x3;
    template <typename Iterator> using error_handler = x3::error_handler<Iterator>;
    using error_handler_tag = x3::error_handler_tag;

    class error_handler_base
    {
     public:
        template <typename Iterator, typename Exception, typename Context> inline x3::error_handler_result on_error(Iterator& first, const Iterator& last, const Exception& x, const Context& context)
            {
                auto& error_handler = x3::get<error_handler_tag>(context).get();
                error_handler(x.where(), "Parsing failed, expecting: " + x.which() + " here:");
                return x3::error_handler_result::fail;
            }
    };
}

namespace parser
{
    namespace x3 = boost::spirit::x3;
    using x3::ascii::char_;

    struct NodeElement;
    struct Node;
    struct Tree;

    x3::rule<NodeElement, ast::NodeElement> const node_element = "node_element";
    x3::rule<Node, ast::Node> const node = "node";
    x3::rule<Tree, ast::Tree> const tree = "tree";

    const auto label = x3::lexeme[+(char_ - char_(" \n:(),;"))];
    const auto branch_length = ':' > x3::double_;

    auto const node_element_def = label | ('(' > (node % ',') > ')');
    auto const node_def = node_element > -branch_length;
    auto const tree_def = node > ';';

    BOOST_SPIRIT_DEFINE(node_element, node, tree);

    struct NodeElement : x3::annotate_on_success, error_handler_base {};
    struct Node : x3::annotate_on_success, error_handler_base {};
    struct Tree : x3::annotate_on_success, error_handler_base {};

    typedef x3::rule<Tree, ast::Tree> tree_type;
    BOOST_SPIRIT_DECLARE(tree_type);

    typedef x3::phrase_parse_context<x3::ascii::space_type>::type phrase_context_type;
    typedef x3::with_context<error_handler_tag, std::reference_wrapper<error_handler<std::string::const_iterator>> const, phrase_context_type>::type context_type;

    BOOST_SPIRIT_INSTANTIATE(tree_type, std::string::const_iterator, context_type);
}

#pragma GCC diagnostic pop

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

    if (success) {
        if (iter != input.end()) {
            error_handler(iter, "Error! Expecting end of input here: ");
        }
        else {
            std::cout << "-------------------------\n";
            std::cout << "Parsing succeeded\n";
              // std::cout << "got: " << my_tree << std::endl;
            std::cout << "\n-------------------------\n";
        }
    }
    else {
        std::cerr << "-------------------------\n";
        std::cerr << "Parsing failed\n";
        std::cerr << "-------------------------\n";
    }

    return 0;
}

// ----------------------------------------------------------------------
/// Local Variables:
/// eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
/// End:
