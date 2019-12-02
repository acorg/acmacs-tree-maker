# -*- Python -*-
# license
# license.
# ======================================================================

import logging; module_logger = logging.getLogger(__name__)
from pathlib import Path
import re, time as time_m, operator, subprocess
from . import htcondor, maker_base

# ----------------------------------------------------------------------

class RaxmlNG (maker_base.MakerBase):

    def __init__(self, config):
        super().__init__(config)
        self.args = [
            "--search",         # (raxml: -f d) run topology search to find the best-scoring ML tree
            "--model", "GTR+G+I", # raxml: -m GTRGAMMAI -c 4
            "--msa", "{source}",   # source fasta
            "--msa-format", "FASTA",
            "--outgroup", "{outgroup}",
            "--tree", "pars{{1}}",
            "--seed", "{seed}",
            "--prefix", "{output_dir}/{run_id}",
            "--log", "PROGRESS", # VERBOSE, DEBUG
            "--threads", "{threads}",
            ]
            # "--silent", "--no-seq-check"
            # -w /syn/eu/ac/results/signature-pages/2019-1007/h3/raxml -e 0.001 -N 1 --stop-after-seconds 1 -o AH3N2/BRISBANE/10/2007_MDCKx -D -n 2019-1007-h3.0000 -p 254251598

    def prepare(self, state):
        # from . import htcondor
        working_dir = Path(state["working_dir"])
        output_dir = working_dir.joinpath("raxmlng")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_dir = output_dir.resolve()
        num_runs = self.config["raxmlng_num_runs"]
        run_id_prefix = (working_dir.parent.name + "-" + working_dir.name).replace(" ", "-")
        state["raxmlng"] = {
            "program": "/syn/bin/raxml-ng",
            "output_dir": str(output_dir),
            "condor_log": str(output_dir.joinpath("condor.log")),
            "run_ids": ["{}.{:04d}".format(run_id_prefix, run_no) for run_no in range(num_runs)],
            }
        state["raxmlng"]["submitted_tasks"] = len(state["raxmlng"]["run_ids"])

        def make_args(**args):
            return [arg.format(**args) for arg in self.args]
        args = [make_args(source=self.config["source"], outgroup=state["outgroup"], seed=self.random_seed(), output_dir=state["raxmlng"]["output_dir"], run_id=run_id, threads=1) for run_id in state["raxmlng"]["run_ids"]]

        state["raxmlng"]["desc"], state["raxmlng"]["condor_log"] = htcondor.prepare_submission(
            program=state["raxmlng"]["program"],
            program_args=args,
            priority=-10,
            description=f"raxml-ng {run_id_prefix} {num_runs}",
            current_dir=output_dir,
            request_memory=1000,
            request_cpus=2,     # avoid using hyperthreading
            capture_stdout=False, email=self.config["email"], notification="Error", machines=self.config["machines"] or None)
        state["state"] = "raxml_submission_prepared"

    def submit(self, state):
        module_logger.info(state["raxmlng"]["desc"])
        state["raxmlng"]["cluster"] = htcondor.submit(state["raxmlng"]["desc"])
        state["raxmlng"]["started"] = time_m.time()
        state["state"] = "raxml_submitted"

    def wait(self, state):
        job = htcondor.Job(clusters=state["raxmlng"]["cluster"], condor_log=state["raxmlng"]["condor_log"])
        status  = job.wait(timeout=self.config["wait_timout"])
        if status == "done":
            state["raxmlng"]["overall_time"] = time_m.time() - state["raxmlng"]["started"]
            module_logger.info("RaXML jobs completed in " + maker_base.Result.time_str(state["raxmlng"]["overall_time"]))

    def make_results(self, state):
        raxml_results = RaxmlNGResults(config=self.config, state=state).read()
        raxml_results.make_txt(Path(state["working_dir"], "result.raxml.txt"))
        raxml_results.make_json(Path(state["working_dir"], "result.raxml.json"))
        state["source_tree"] = raxml_results.best_tree()
        return raxml_results

# ----------------------------------------------------------------------

class RaxmlNGResult (maker_base.Result):

    sBestScore = re.compile(r"Final LogLikelihood: -([\d\.]+)", re.I)
    sElapsedTime = re.compile(r"Elapsed time: ([\d\.]+) seconds", re.I)

    def __init__(self, best_tree):
        super().__init__()
        if best_tree is not None:
            self.read(best_tree)

    def read(self, best_tree):
        self.tree = best_tree
        self.run_id = ".".join(best_tree.name.split(".")[:2])
        log_file = best_tree.parent.joinpath(f"{self.run_id}.raxml.log")
        log = log_file.open().read()
        m_score = self.sBestScore.search(log)
        if m_score:
            self.score = float(m_score.group(1))
        else:
            raise ValueError(f"Raxml: cannot extract best score from {log_file}")
        m_time = self.sElapsedTime.search(log)
        if m_time:
            self.time = float(m_time.group(1))
        else:
            self.time = None

    def tabbed_report(self):
        return "{:10.4f} {:>8s} {}".format(self.score, self.time_str(self.time), str(self.tree))

# ----------------------------------------------------------------------

class RaxmlNGResults (maker_base.Results):

    def read(self):
        self.results = sorted((RaxmlNGResult(best_tree) for best_tree in Path(self.state["raxmlng"]["output_dir"]).glob("*.raxml.bestTree")), key=operator.attrgetter("score"))
        self.longest_time = max(self.results, key=operator.attrgetter("time")).time if self.results else 0
        self.overall_time = self.state["raxmlng"]["overall_time"]
        self.submitted_tasks = self.state["raxmlng"]["submitted_tasks"]
        return self

    def tabbed_report_header(cls):
        return "{:^10s} {:^8s} {:^10s} {}".format("score", "time", "endscore", "tree")

    def result_class(self):
        return RaxmlNGResult

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
