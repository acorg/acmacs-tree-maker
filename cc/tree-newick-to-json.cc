#include <iostream>
#include <string>
#include <vector>
#include <map>

// ----------------------------------------------------------------------
// ----------------------------------------------------------------------

#pragma GCC diagnostic push
#include "acmacs-base/boost-diagnostics.hh"
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
                error_handler(x.where(), "ERROR: parsing failed, expecting: " + x.which() + " here:");
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
// ----------------------------------------------------------------------

#include "acmacs-base/json-writer.hh"

static constexpr const char* TREE_JSON_DUMP_VERSION = "newick-tree-v1";

class if_non_negative
{
 public:
    inline if_non_negative(const char* key, double value) : mKey(key), mValue(value) {}

    template <typename RW> friend inline JsonWriterT<RW>& operator <<(JsonWriterT<RW>& writer, const if_non_negative& data)
        {
            if (data.mValue >= 0.0)
                writer << JsonObjectKey(data.mKey) << data.mValue;
            return writer;
        }

 private:
    const char* mKey;
    double mValue;
};

template <typename RW> class NodeElementWriter
{
 public:
    inline NodeElementWriter(JsonWriterT<RW>& aWriter) : mWriter(aWriter) {}

    inline void operator()(const ast::Label& aLabel) const { mWriter << JsonObjectKey("n") << aLabel; }
    inline void operator()(const std::vector<ast::Node>& aNodes) const { mWriter << JsonObjectKey("t") << aNodes; }

 private:
    JsonWriterT<RW>& mWriter;
};

template <typename RW> inline JsonWriterT<RW>& operator <<(JsonWriterT<RW>& writer, const ast::NodeElement& node_element)
{
    boost::apply_visitor(NodeElementWriter<RW>{writer}, node_element);
    return writer;
}

template <typename RW> inline JsonWriterT<RW>& operator <<(JsonWriterT<RW>& writer, const ast::Node& node)
{
    return writer << StartObject
            << node.element
            << if_non_negative("l", node.length)
            << EndObject;
}

template <typename RW> inline JsonWriterT<RW>& operator <<(JsonWriterT<RW>& writer, const ast::Tree& tree)
{
    return writer << StartObject
                  << JsonObjectKey("  version") << TREE_JSON_DUMP_VERSION
                  << JsonObjectKey("tree") << static_cast<const ast::Node>(tree)
                  << EndObject;
}

inline std::ostream& operator << (std::ostream& out, const ast::Tree& tree)
{
    return out << json(tree, "newick-tree", 1);
}

// ----------------------------------------------------------------------
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
