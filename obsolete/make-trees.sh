#! /usr/bin/env bash

SUBTYPES="h1 h3 bv by"
if [[ $# -eq 1 ]]; then
    SUBTYPES="$1"
fi

# ======================================================================

declare -A BASE_SEQS
declare -A PREPEND
declare -A SEQDB3_ARGS
declare -A TITLE

# ---------- H1 ----------
BASE_SEQS[h1]="AH1N1/MICHIGAN/45/2015_QMC2MDCK3"
PREPEND[h1]=()
SEQDB3_ARGS[h1]="--flu h1 --recent-matched 3000,4000 --host human --nuc-hamming-distance-threshold 160"
TITLE[h1]="tree H1"

# ---------- H3 ----------
# --> 3a clade is in the middle of the tree, surrounded by 2a subclades
# BASE_SEQS[h3]="SWITZERLAND/8060/2017 SIAT2"
#
# [2020-01-17] trying 3C.3A base seq from the end of 2017
# seqdb3 --flu h3 --whocc-lab --clade 3C.3A --start-date 2017-10-01 --end-date 2018 -p
# A\\(H3N2\\)/ is necessary to avoid selecting AH3N2/ARKANSAS/14/2017_OR
# --> leads to 3a subtree having much shorted edges than 2a subtree
# BASE_SEQS[h3]="A\\(H3N2\\)/KANSAS/14/2017 OR"
#
# [2020-01-24] Derek: the h3 tree should be rooted with an older than 3c.3a and older than 3c.2a strain
# seqdb3 --flu h3 --start-date 2017 --end-date 2017-02 -p --whocc-lab --with-hi-name | grep -v '3C.[123]'
# --> 2a3 clade is above 3a clade and closer to the outgroup
# BASE_SEQS[h3]="AH3N2/HAWAII/3/2017_OR"

# [2020-01-27]
# seqdb3 --flu h3 --start-date 2016 --end-date 2016-04 -p --whocc-lab --with-hi-name | grep -v '3C.[123]'
# --> seems to be worse than A/HAWAII/3/2017 case, 2a2 is above 3a
# BASE_SEQS[h3]="A\\(H3N2\\)/NEW YORK/60/2016"

# [2020-02-06]
# intermediate strains from nextflu https://nextstrain.org/flu/seasonal/h3n2/ha/2y
# to keep 3a at the top
#
# Stockholm/6/2014            2014-02-06    3c3            AH3N2/STOCKHOLM/6/2014_OR
#
# Switzerland/9715293/2013    2013-12-06    3a             AH3N2/SWITZERLAND/9715293/2013_SIAT1/SIAT2/SIAT1
# Norway/466/2014             2014-02-03    3a             AH3N2/NORWAY/466/2014_SIAT1SIAT1/SIAT1
# South Australia/55/2014     2014-06-29    3a             AH3N2/SOUTH_AUSTRALIA/55/2014_MDCK1/
# Tasmania/11/2014            2014-03-16    3a             AH3N2/TASMANIA/11/2014_MDCK1
# Kobe/63/2014                2014-05-21    3a             AH3N2/KOBE/63/2014_MDCK1
# Peru/27/2015                2015-04-13    3a             AH3N2/PERU/27/2015_MDCK2/SIAT1
# Nevada/22/2016              2016-03-05    3a             AH3N2/NEVADA/22/2016_OR
# Idaho/33/2016               2016-06-08    3a             AH3N2/IDAHO/33/2016_OR
# Texas/88/2016               2016-02-25    3a             AH3N2/TEXAS/88/2016_OR
# Texas/71/2017               2017-03-18    3a             AH3N2/TEXAS/71/2017_OR
# Brazil/7331/2018            2018-07-09    3a             AH3N2/BRAZIL/7331/2018_OR
#
# Hong Kong/4801/2014         2014-02-26    2a             AH3N2/HONG_KONG/4801/2014_MDCK4/SIAT4
# Hawaii/47/2014              2014-07-18    2a             AH3N2/HAWAII/47/2014_SIAT3
#
# North Carolina/4/2017       2017-01-26    2a2            AH3N2/NORTH_CAROLINA/4/2017_OR
#
# North Carolina/4/2016       2016-01-14    2a1            AH3N2/NORTH_CAROLINA/4/2016_OR
# Antananarivo/1067/2016      2016-04-06    2a1            AH3N2/ANTANANARIVO/1067/2016_OR
#
# Hong Kong/2286/2017         2017-05-23    2a1b 135K      AH3N2/HONG_KONG/2286/2017_MDCKx/SIAT1
# Wisconsin/327/2017          2017-09-22    2a1b 135K      AH3N2/WISCONSIN/327/2017_OR
# Abu Dhabi/240/2018          2018-01-01    2a1b 135K      AH3N2/ABU_DHABI/240/2018_OR
#
# Jamaica/1447/2018           2018-02-19    2a1b 131K      AH3N2/JAMAICA/1447/2018_OR
BASE_SEQS[h3]="AH3N2/STOCKHOLM/6/2014_OR"
PREPEND[h3]=(AH3N2/SWITZERLAND/9715293/2013_SIAT1/SIAT2/SIAT1 AH3N2/NORWAY/466/2014_SIAT1SIAT1/SIAT1 AH3N2/SOUTH_AUSTRALIA/55/2014_MDCK1/)

SEQDB3_ARGS[h3]="--flu h3 --recent-matched 3000,4000 --host human --nuc-hamming-distance-threshold 160"
TITLE[h3]="tree H3"

# ---------- BVic ----------
BASE_SEQS[bv]="B/VICTORIA/830/2013_MDCK2"
PREPEND[bv]=()
SEQDB3_ARGS[bv]="--whocc-lab --flu b --lineage vic --recent 7000 --nuc-hamming-distance-threshold 160"
TITLE[bv]="tree B/Vic"

# ---------- BYam ----------
BASE_SEQS[by]="B/NEW_HAMPSHIRE/1/2016_E5"
PREPEND[by]=()
SEQDB3_ARGS[by]="--flu b --lineage yam --recent-matched 4000,3000 --nuc-hamming-distance-threshold 160"
TITLE[by]="tree B/Yam"

SEQDB3_COMMON_ARGS="--db ../seqdb.json.xz --nucs --wrap --most-common-length --name-format '{seq_id}'"

# ======================================================================

echo seqdb --base-seq-id '${BASE_SEQS[h3]}'
exit 1

set -x
DATE=$(date +%Y-%m%d)
ROOT_DIR=/syn/eu/ac/results/signature-pages/${DATE}
echo ${ROOT_DIR}
mkdir -p ${ROOT_DIR}
cd ${ROOT_DIR}
cp "${ACMACSD_ROOT}/data/seqdb.json.xz" .

for vir in ${SUBTYPES}; do
    mkdir -p "${vir}"
    cat >"${vir}-export.sh" <<EOF
#! /bin/bash
seqdb3 ${SEQDB3_COMMON_ARGS} ${SEQDB3_ARGS[${vir}]} --base-seq-id '${BASE_SEQS[${vir}]}' --fasta source.fas
EOF
    chmod +x "${vir}-export.sh"
    pane=$(tmux new-window -c "${ROOT_DIR}" -n "${TITLE[${vir}]}" -P)
    tmux send-keys -t "${pane}" "cd ${vir} && ../${vir}-export.sh && tree-maker init && mg tree-maker.config && echo tree-maker wait" Enter
done
