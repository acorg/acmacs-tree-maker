#pragma once

#include <iostream>

#include "acmacs-base/json-writer.hh"

// ----------------------------------------------------------------------

static constexpr const char* TREE_JSON_DUMP_VERSION = "newick-tree-v1";

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

inline std::string tree_to_json(const ast::Tree& tree)
{
    return json(tree, TREE_JSON_DUMP_VERSION, 1);
}

inline std::ostream& operator << (std::ostream& out, const ast::Tree& tree)
{
    return out << tree_to_json(tree);
}

// ----------------------------------------------------------------------
/// Local Variables:
/// eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
/// End:
