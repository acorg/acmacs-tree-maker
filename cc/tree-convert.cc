#include <iostream>
#include <string>
#include <vector>
#include <stack>

#pragma GCC diagnostic push
#ifdef __clang__
#pragma GCC diagnostic ignored "-Wshadow"
#pragma GCC diagnostic ignored "-Wexit-time-destructors"
#pragma GCC diagnostic ignored "-Wdeprecated"
#pragma GCC diagnostic ignored "-Wglobal-constructors"
#pragma GCC diagnostic ignored "-Wextra-semi"
#pragma GCC diagnostic ignored "-Wold-style-cast"
#pragma GCC diagnostic ignored "-Wsign-conversion"
#pragma GCC diagnostic ignored "-Wundef"
#endif
#include "boost/spirit/home/x3.hpp"

#include <boost/fusion/include/adapt_struct.hpp>
#pragma GCC diagnostic pop


// ----------------------------------------------------------------------

struct ptree;
typedef std::vector<ptree> children_t;

struct ptree
{
    children_t children;
    std::string name;
    double length;
};

inline std::ostream& operator<<(std::ostream& stream, const ptree& tree)
{
    bool first = true;
    stream << "(" << tree.name << ": " << tree.length << " { ";
    for (const auto& child: tree.children)
    {
        stream << (first ? "" : "," ) << child;
        first = false;
    }
    return stream << " }";
}

#ifdef __clang__
#pragma GCC diagnostic ignored "-Wdisabled-macro-expansion"
#endif

BOOST_FUSION_ADAPT_STRUCT(
    ptree,
    (children_t, children)
    (std::string, name)
    (double, length)
)

// ----------------------------------------------------------------------

using boost::spirit::x3::rule;

struct newick_grammar : boost::spirit::x3::grammar<std::string::const_iterator, ptree()>
{
 public:
    newick_grammar()
        : newick_grammar::base_type(tree) // We try to parse the tree rule
        {
            using boost::spirit::x3::lexeme;
            using boost::spirit::x3::double_;
            using boost::spirit::x3::char_;
            using boost::spirit::x3::_val;
            using boost::mpl::_1;

            using phoenix::at_c; // Access nth field of structure
            using phoenix::push_back; // Push into vector

              // For label use %= to assign the result of the parse to the string
            label %= lexeme[+(char_ - ':' - ')' - ',')];

              // For branch length use %= to assign the result of the parse to the
              // double
            branch_length %= ':' >> double_;

              // When parsing the subtree just assign the elements that have been
              // built in the subrules
            subtree =
                      // Assign vector of children to the first element of the struct
                    -descendant_list [at_c<0>(_val) = _1 ]
                      // Assign the label to the second element
                    >> -label [ at_c<1>(_val) = _1 ]
                      // Assign the branch length to the third element
                    >> -branch_length [ at_c<2>(_val) = _1 ];

              // Descendant list is a vector of ptree, we just push back the
              // created ptrees into the vector
            descendant_list =
                    '(' >> subtree [ push_back(_val, _1) ]
                        >> *(',' >> subtree [ push_back(_val, _1) ])
                        >> ')';

              // The tree receive the whole subtree using %=
            tree %= subtree  >> ';' ;
        }

 private:

      // Here are the various grammar rules typed by the element they do
      // generate
    rule<std::string::const_iterator, ptree()> tree, subtree;
    rule<std::string::const_iterator, children_t()> descendant_list;
    rule<std::string::const_iterator, double()> branch_length;
    rule<std::string::const_iterator, std::string()> label;
};


// ----------------------------------------------------------------------

template <typename Iterator> bool parse_newick(Iterator first, Iterator last, ptree& tree)
{
    using boost::spirit::x3::double_;
    using boost::spirit::x3::_attr;
    using boost::spirit::x3::phrase_parse;
    using boost::spirit::x3::ascii::space;

    double rN = 0.0;
    double iN = 0.0;
    auto fr = [&](auto& ctx){ rN = _attr(ctx); };
    auto fi = [&](auto& ctx){ iN = _attr(ctx); };

    bool r = phrase_parse(first, last,

                            //  Begin grammar
                          (
                              '(' >> double_[fr]
                              >> -(',' >> double_[fi]) >> ')'
                              |   double_[fr]
                           ),
                            //  End grammar

                          space);

    if (!r || first != last) // fail if we did not get a full match
        return false;
      //c = std::complex<double>(rN, iN);
    return r;
}

// ----------------------------------------------------------------------

int main()
{
    ptree root;
    std::string input(std::istream_iterator<char>{std::cin}, std::istream_iterator<char>{});
    if (parse_newick(input.begin(), input.end(), root))
    {
        std::cout << "-------------------------\n";
        std::cout << "Parsing succeeded\n";
        std::cout << "got: " << root << std::endl;
        std::cout << "\n-------------------------\n";
    }
    else
    {
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
