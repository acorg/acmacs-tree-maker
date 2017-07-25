#pragma once

#include <iostream>

namespace json_writer
{
    template <typename RW> class writer;
}
namespace jsw = json_writer;

template <typename RW> inline jsw::writer<RW>& operator <<(jsw::writer<RW>&, const ast::NodeElement&);
template <typename RW> inline jsw::writer<RW>& operator <<(jsw::writer<RW>&, const ast::Node&);
template <typename RW> inline jsw::writer<RW>& operator <<(jsw::writer<RW>&, const ast::Tree&);

#include "acmacs-base/json-writer.hh"

// ----------------------------------------------------------------------

static constexpr const char* TREE_JSON_DUMP_VERSION = "newick-tree-v1";

template <typename RW> class NodeElementWriter
{
 public:
    inline NodeElementWriter(jsw::writer<RW>& aWriter) : mWriter(aWriter) {}

    inline void operator()(const ast::Label& aLabel) const { mWriter << jsw::key("n") << aLabel; }
    inline void operator()(const std::vector<ast::Node>& aNodes) const { mWriter << jsw::key("t") << aNodes; }

 private:
    jsw::writer<RW>& mWriter;
};

template <typename RW> inline jsw::writer<RW>& operator <<(jsw::writer<RW>& writer, const ast::NodeElement& node_element)
{
    boost::apply_visitor(NodeElementWriter<RW>{writer}, node_element);
    return writer;
}

template <typename RW> inline jsw::writer<RW>& operator <<(jsw::writer<RW>& writer, const ast::Node& node)
{
    return writer << jsw::start_object
            << node.element
            << jsw::if_non_negative("l", node.length)
            << jsw::end_object;
}

template <typename RW> inline jsw::writer<RW>& operator <<(jsw::writer<RW>& writer, const ast::Tree& tree)
{
    return writer << jsw::start_object
                  << jsw::key("  version") << TREE_JSON_DUMP_VERSION
                  << jsw::key("tree") << static_cast<const ast::Node>(tree)
                  << jsw::end_object;
}

inline std::string tree_to_json(const ast::Tree& tree)
{
    return jsw::json(tree, 1);
}

inline std::ostream& operator << (std::ostream& out, const ast::Tree& tree)
{
    return out << tree_to_json(tree);
}

// ----------------------------------------------------------------------
/// Local Variables:
/// eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
/// End:
