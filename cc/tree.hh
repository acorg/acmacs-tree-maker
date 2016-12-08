#pragma once

#include <string>
#include <vector>

#pragma GCC diagnostic push
#include "acmacs-base/boost-diagnostics.hh"
#define BOOST_SPIRIT_X3_NO_FILESYSTEM 1
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

// ----------------------------------------------------------------------

namespace ast
{
    namespace x3 = boost::spirit::x3;
    struct Node;

    struct Label : public std::string {};

    struct NodeElement : public x3::variant<Label, std::vector<Node>>
    {
        using base_type::base_type;
        using base_type::operator=;
    };

    struct Node
    {
        inline Node() : length(-1) {}

        NodeElement element;
        double length;
    };

    struct Tree : public Node
    {
    };
}

// ----------------------------------------------------------------------

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

// ----------------------------------------------------------------------

#pragma GCC diagnostic pop

// ----------------------------------------------------------------------
/// Local Variables:
/// eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
/// End:
