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
            module_logger.info("RaXML jobs completed in " + RaxmlResult.time_str(state["raxmlng"]["overall_time"]))

    def analyse_logs(self, state):
        module_logger.warning(f"RaxmlNG.analyse_logs not implemented")

        # def load_log_file(filepath):
        #     for attempt in range(10):
        #         try:
        #             r = [{"t": float(e[0]), "s": -float(e[1]), "f": str(filepath).split(".")[-1]} for e in (line.strip().split() for line in filepath.open())]
        #             if not r:   # pending
        #                 r = [{"t": 0, "s": 0}]
        #             return r
        #         except ValueError as err:
        #             pass        # file is being written at the moment, try again later
        #             module_logger.info('(ignored) cannot process {}: {}'.format(filepath.name, err))
        #         time_m.sleep(3)
        #     raise RuntimeError("Cannot process {}".format(filepath))

        # def time_score_from_log(files):
        #     return min((load_log_file(filepath)[-1] for filepath in files), key=operator.itemgetter("s"))

        # completed = [run_id for run_id in state["raxmlng"]["run_ids"] if Path(state["raxmlng"]["output_dir"], "RAxML_bestTree." + run_id).exists()]
        # if completed:
        #     best_completed = time_score_from_log(Path(state["raxmlng"]["output_dir"], "RAxML_log." + run_id) for run_id in completed)
        #     # module_logger.info('completed: {} best: {}'.format(len(completed), best_completed))
        #     running_logs = [f for f in (Path(state["raxmlng"]["output_dir"], "RAxML_log." + run_id) for run_id in state["raxmlng"]["run_ids"] if run_id not in completed) if f.exists()]
        #     data = {int(str(f).split(".")[-1]): load_log_file(f) for f in running_logs}
        #     scores_for_longer_worse_than_best_completed = {k: v[-1]["s"] for k, v in data.items() if v[-1]["t"] > best_completed["t"] and v[-1]["s"] > best_completed["s"]}
        #     by_score = sorted(scores_for_longer_worse_than_best_completed, key=lambda e: scores_for_longer_worse_than_best_completed[e])
        #     n_to_kill = int(len(by_score) * self.config["raxml_kill_rate"])
        #     if n_to_kill > 0:
        #         to_kill = by_score[-n_to_kill:]
        #         module_logger.info('completed: {} best: {} worse_than_best_completed: {} to kill: {}'.format(len(completed), best_completed, by_score, to_kill))
        #         job = htcondor.Job(clusters=state["raxmlng"]["cluster"], condor_log=state["raxmlng"]["condor_log"])
        #         job.kill_tasks(to_kill)
        #         run_id_to_del = [ri for ri in state["raxmlng"]["run_ids"] if int(ri.split(".")[-1]) in to_kill]
        #         # module_logger.info('run_id_to_del {}'.format(run_id_to_del))
        #         for ri in run_id_to_del:
        #             state["raxmlng"]["run_ids"].remove(ri)
        #         state["raxmlng"]["survived_tasks"] -= len(run_id_to_del)
        #         # module_logger.info('To kill {}: {} run_ids left: {}'.format(n_to_kill, to_kill, state["raxmlng"]["run_ids"]))
        #         # module_logger.info('To kill {}: {}'.format(n_to_kill, to_kill))
        #     # else:
        #     #     module_logger.info('Nothing to kill')

    def make_results(self, state):
        raise RuntimeError("RaxmlNG.make_results not implemented")

        # raxml_results = RaxmlNGResults(config=self.config, state=state).read()
        # raxml_results.make_txt(Path(state["working_dir"], "result.raxml.txt"))
        # raxml_results.make_json(Path(state["working_dir"], "result.raxml.json"))
        # raxml_results.make_r_score_vs_time()
        # state["source_tree"] = raxml_results.best_tree()
        # return raxml_results

# ----------------------------------------------------------------------

class RaxmlNGResult (maker_base.Result):

    sInfoBestScore = re.compile(r"Final GAMMA-based Score of best tree -([\d\.]+)", re.I)
    sInfoExecutionTime = re.compile(r"Overall execution time: ([\d\.]+) secs ", re.I)

    def __init__(self, best_tree):
        super().__init__()
        if best_tree is not None:
            self.read(best_tree)

    def read(self, best_tree):
        self.tree = best_tree
        self.run_id = ".".join(best_tree.parts[-1].split(".")[1:])
        info_data = best_tree.parent.joinpath("RAxML_info." + self.run_id).open().read()
        m_score = self.sInfoBestScore.search(info_data)
        if m_score:
            self.score = float(m_score.group(1))
        else:
            raise ValueError("Raxml: cannot extract best score from " + str(Path(output_dir, "RAxML_info." + self.run_id)))
        m_time = self.sInfoExecutionTime.search(info_data)
        if m_time:
            self.time = float(m_time.group(1))
        else:
            self.time = None
        log_data = best_tree.parent.joinpath("RAxML_log." + self.run_id).open().readlines()
        self.start_scores = [- float(log_data[0].split()[1]), - float(log_data[-1].split()[1])]

    def tabbed_report(self):
        return "{:10.4f} {:>8s} {:10.4f} {:10.4f} {}".format(self.score, self.time_str(self.time), self.start_scores[0], self.start_scores[1], str(self.tree))

# ----------------------------------------------------------------------

class RaxmlNGResults (maker_base.Results):

    # def __init__(self, results, overall_time, submitted_tasks, survived_tasks):
    #     super().__init__(results=results, overall_time=overall_time, submitted_tasks=submitted_tasks, survived_tasks=survived_tasks)

    def read(self):
        self.results = sorted((RaxmlNGResult(best_tree) for best_tree in Path(self.state["raxmlng"]["output_dir"]).glob("RAxML_bestTree.*")), key=operator.attrgetter("score"))
        self.longest_time = max(self.results, key=operator.attrgetter("time")).time if self.results else 0
        self.overall_time = self.state["raxmlng"]["overall_time"]
        self.submitted_tasks = self.state["raxmlng"]["submitted_tasks"]
        self.survived_tasks = self.state["raxmlng"]["survived_tasks"]
        return self

    def max_start_score(self):
        max_e_all = max(self.results, key=lambda e: max(e.score, *e.start_scores))
        return max(max_e_all.score, *max_e_all.start_scores)

    def tabbed_report_header(cls):
        return "{:^10s} {:^8s} {:^10s} {:^10s} {}".format("score", "time", "startscore", "endscore", "tree")

    def make_r_score_vs_time(self):
        filepath = Path(self.state["working_dir"], "raxml.score-vs-time.r")
        module_logger.info('Generating {}'.format(filepath))
        colors = {k.tree: c for k, c in zip(self.results, ["green", "cyan", "blue"])}
        if len(self.results) > 3:
            colors[self.results[-1].tree] = "red"
        with filepath.open("w") as f:
            f.write('doplot <- function(lwd) {\n')
            f.write('    plot(c(0, {longest_time}), c({min_score}, {max_score}), type="n", xlab="time (hours)", ylab="RAxML score", main="RAxML processing" )\n'.format(
                longest_time=self.longest_time / 3600,
                min_score=-self.results[0].score,
                max_score=-self.max_start_score()
                # max_score=-self.results[-1].score,
                ))
            f.write('    legend("bottomright", lwd=5, legend=c({trees}), col=c({colors}))\n'.format(
                trees=",".join(repr(str(t).split("/")[-1]) for t in sorted(colors)),
                colors=",".join(repr(colors[t]) for t in sorted(colors))))
            for r_e in reversed(self.results): # reversed for the best score line appear on top
                f.write('    d <- read.table("{log}")\n'.format(log=str(r_e.tree).replace("/RAxML_bestTree.", "/RAxML_log.")))
                f.write('    dlen <- length(d$V1)\n')
                f.write('    d$V1 <- d$V1 / 3600\n')
                color = colors.get(r_e.tree, "grey")
                f.write('    lines(d, col="{color}", lwd=lwd)\n'.format(color=color))
                f.write('    points(d$V1[dlen], d$V2[dlen], col="black")\n')
            f.write('}\n\n')
            f.write('pdf("{fn}", 10, 10)\n'.format(fn=filepath.with_suffix(".pdf")))
            f.write('doplot(lwd=0.1)\n')
            f.write('dev.off()\n\n')
            # f.write('png("{fn}", 1200, 1200)\n'.format(fn=filepath.with_suffix(".png")))
            # f.write('doplot(lwd=0.5)\n')
            # f.write('dev.off()\n\n')
        subprocess.run(["Rscript", str(filepath)], stdout=subprocess.DEVNULL)
        module_logger.info('Plot {} generated'.format(filepath.with_suffix(".pdf")))

    def result_class(self):
        return RaxmlResult

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
