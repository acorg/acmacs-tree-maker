# -*- Python -*-
# license
# license.
# ======================================================================

import logging; module_logger = logging.getLogger(__name__)
from pathlib import Path
import random
from . import htcondor

# ----------------------------------------------------------------------

class Raxml:

    def __init__(self, config):
        self.config = config
        self.default_args = ["-c", "4", "-f", "d", "--silent", "--no-seq-check"]
        self.random_gen = random.SystemRandom()

    def random_seed(self):
        return self.random_gen.randint(1, 0xFFFFFFF)   # note max for garli is 0x7ffffffe

    def prepare(self, state):
        # from . import htcondor
        working_dir = Path(state["working_dir"])
        output_dir = working_dir.joinpath("raxml")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_dir = output_dir.resolve()
        state["raxml"] = {
            "program": "/syn/bin/raxml",
            "output_dir": str(output_dir),
            "model": "GTRGAMMAI",
            "condor_log": str(output_dir.joinpath("condor.log")),
            }
        general_args = ["-s", self.config["source"], "-w", state["raxml"]["output_dir"], "-m", state["raxml"]["model"], "-e", str(self.config["raxml_model_optimization_precision"]),
                            "-T", "1", "-N", "1"] + self.default_args
        # if source_tree is not None:
        #     general_args += ["-t", str(source_tree)]
        # if outgroups:
        #     general_args += ["-o", ",".join(outgroups)]
        num_runs = self.config["raxml_num_runs"]
        run_id = (working_dir.parent.name + "-" + working_dir.name).replace(" ", "-")
        run_ids = ["{}.{:04d}".format(run_id, run_no) for run_no in range(num_runs)]
        args = [(general_args + ["-n", ri, "-p", str(self.random_seed())]) for ri in run_ids]
        state["raxml"]["desc"] = htcondor.prepare_submission(
            program=state["raxml"]["program"],
            program_args=args,
            description="RAxML {run_id} {num_runs}".format(run_id=run_id, num_runs=num_runs,),
            current_dir=output_dir,
            capture_stdout=False, email=self.config["email"], notification="Error", machines=self.config["machines"] or None)
        state["state"] = "raxml_submission_prepared"

    def submit(self, state):
        state["raxml"]["cluster"] = htcondor.submit(state["raxml"]["desc"])
        state["state"] = "raxml_submitted"

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
