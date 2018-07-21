# -*- Python -*-
# license
# license.
# ======================================================================

import logging; module_logger = logging.getLogger(__name__)
from pathlib import Path
import getpass
from acmacs_base import json

# ----------------------------------------------------------------------

sDefault = {
    "source": "",
    "mode?": ["raxml_survived_best_garli", "raxml_best_garli", "raxml_all_garli"],
    "mode": "raxml_survived_best_garli",
    "wait_timout": 60,
    "raxml_kill_rate?": ">0, <=1",
    "raxml_kill_rate": 0.5,
    "raxml_bfgs": True,
    "raxml_D": True,
    "raxml_D?": "-D ML search convergence criterion. On trees with more than 500 taxa this will yield execution time improvements of approximately 50% while yielding only slightly worse trees.",
    "raxml_model_optimization_precision?": "see RAxML -e switch, higher values allows faster RAxML run but give worse score",
    "raxml_model_optimization_precision": 0.001,
    "raxml_num_runs?": "number of runs of RAxML with different random seeds",
    "raxml_num_runs": 256,
    "garli_num_runs?": "number of runs of GARLI with different random seeds",
    "garli_num_runs": 256,
    "garli_attachmentspertaxon?": "GARLI: the number of attachment branches evaluated for each taxon to be added to the tree during the creation of an ML stepwise-addition starting tree (when garli is run without raxml step)",
    "garli_attachmentspertaxon": 1000000,
    "garli_stoptime?": "GARLI termination condition: the maximum number of seconds for the run to continue (default value is a week)",
    "garli_stoptime": 60*60*24*7,
    "garli_genthreshfortopoterm?": "GARLI termination condition: when no new significantly better scoring topology has been encountered in greater than this number of generations, garli stops",
    "garli_genthreshfortopoterm": 20000,
    "email": getpass.getuser(),
    "machines?": ["odette", "i19", "i20", "i21", "o16", "o17"],
    "machines": ["i20", "i21", "o16", "o17"],
    }

# ----------------------------------------------------------------------

def init(args):
    working_dir = Path(args.working_dir)
    if not working_dir.exists():
        raise RuntimeError("Working dir {!r} does not exist".format(working_dir))
    config = sDefault
    fasta = sorted(working_dir.glob("*.fas*"))
    if not fasta:
        raise RuntimeError("No .fasta file found in working dir {!r}".format(working_dir))
    if len(fasta) > 1:
        module_logger.warning('Multiple fasta files found: {}, the first one will be used.'.format(fasta))
    config["source"] = str(Path(fasta[0]).resolve())
    save(filename=working_dir.joinpath(args.config_file_name), config=config)

# ----------------------------------------------------------------------

def load(filename: Path):
    return json.read_json(filename)

# ----------------------------------------------------------------------

def save(filename: Path, config):
    json.write_json(path=filename, data=config, indent=2, compact=True)

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
