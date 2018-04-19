#pragma once

#include <iostream>

#pragma GCC diagnostic push
#include "acmacs-base/boost-diagnostics.hh"
#include "boost/spirit/home/x3.hpp"
#include "boost/spirit/home/x3/support/ast/position_tagged.hpp"
#include "boost/spirit/home/x3/support/utility/error_reporting.hpp"
#include "boost/spirit/home/x3/support/utility/annotate_on_success.hpp"
#pragma GCC diagnostic pop

#include "tree.hh"

// ----------------------------------------------------------------------

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-parameter" // for clang and gcc 6.2
#ifdef __clang__
#pragma GCC diagnostic ignored "-Wglobal-constructors"
#endif

namespace parser
{
    namespace x3 = boost::spirit::x3;
    template <typename Iterator> using error_handler = x3::error_handler<Iterator>;
    using error_handler_tag = x3::error_handler_tag;

    class error_handler_base
    {
     public:
        template <typename Iterator, typename Exception, typename Context> inline x3::error_handler_result on_error(Iterator& /*first*/, const Iterator& /*last*/, const Exception& x, const Context& context)
            {
                auto& error_handler = x3::get<error_handler_tag>(context).get();
                error_handler(x.where(), "ERROR: parsing failed, expecting: " + x.which() + " here:");
                return x3::error_handler_result::fail;
            }
    };

    struct NodeElement : x3::annotate_on_success, error_handler_base {};
    struct Node : x3::annotate_on_success, error_handler_base {};
    struct Tree : x3::annotate_on_success, error_handler_base {};

    x3::rule<NodeElement, ast::NodeElement> const node_element = "node_element";
    x3::rule<Node, ast::Node> const node = "node";
    x3::rule<Tree, ast::Tree> const tree = "tree";

    using x3::ascii::char_;
    const auto label = x3::lexeme[+(char_ - char_(" \n:(),;"))];
    const auto branch_length = ':' > x3::double_;

    auto const node_element_def = label | ('(' > (node % ',') > ')');
    auto const node_def = node_element > -branch_length;
    auto const tree_def = node > ';';

    BOOST_SPIRIT_DEFINE(node_element, node, tree);

    typedef x3::rule<Tree, ast::Tree> tree_type;
    BOOST_SPIRIT_DECLARE(tree_type);

    typedef x3::phrase_parse_context<x3::ascii::space_type>::type phrase_context_type;
    typedef x3::context<error_handler_tag, std::reference_wrapper<error_handler<std::string::const_iterator>> const, phrase_context_type> context_type;

    BOOST_SPIRIT_INSTANTIATE(tree_type, std::string::const_iterator, context_type);
}

// ----------------------------------------------------------------------

class NewickImportFailed : public std::exception {};

inline void import_newick(std::string input, ast::Tree& tree)
{
    namespace x3 = boost::spirit::x3;
    auto iter = input.begin();
    parser::error_handler<std::string::const_iterator> error_handler{iter, input.end(), std::cerr}; //, "input"};

    auto const pp = x3::with<parser::error_handler_tag>(std::ref(error_handler))[parser::tree];

    if (!phrase_parse(iter, input.end(), pp, x3::ascii::space, tree))
        throw NewickImportFailed{};
    if (iter != input.end()) {
        error_handler(iter, "ERROR: expecting end of input here: ");
        throw NewickImportFailed{};
    }
}

#pragma GCC diagnostic pop

// ----------------------------------------------------------------------
/// Local Variables:
/// eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
/// End:
