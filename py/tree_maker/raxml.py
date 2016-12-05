# -*- Python -*-
# license
# license.
# ======================================================================

import logging; module_logger = logging.getLogger(__name__)
from pathlib import Path
import random, time as time_m
from . import htcondor, maker_base

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
        state["raxml"]["run_ids"] = ["{}.{:04d}".format(run_id, run_no) for run_no in range(num_runs)]
        args = [(general_args + ["-n", ri, "-p", str(self.random_seed())]) for ri in state["raxml"]["run_ids"]]
        state["raxml"]["desc"], state["raxml"]["condor_log"] = htcondor.prepare_submission(
            program=state["raxml"]["program"],
            program_args=args,
            description="RAxML {run_id} {num_runs}".format(run_id=run_id, num_runs=num_runs,),
            current_dir=output_dir,
            capture_stdout=True, email=self.config["email"], notification="Error", machines=self.config["machines"] or None)
        state["state"] = "raxml_submission_prepared"

    def submit(self, state):
        state["raxml"]["cluster"] = htcondor.submit(state["raxml"]["desc"])
        state["raxml"]["started"] = time_m.time()
        state["state"] = "raxml_submitted"

    def wait(self, state):
        job = htcondor.Job(clusters=state["raxml"]["cluster"], condor_log=state["raxml"]["condor_log"])
        status  = job.wait(timeout=self.config["wait_timout"])
        if status == "done":
            state["raxml"]["overall_time"] = time_m.time() - state["raxml"]["started"]
        module_logger.info("RaXML jobs completed in " + RaxmlResult.time_str(state["raxml"]["overall_time"]))

    def analyse_logs(self, state):
        def load_log_file(filepath):
            for attempt in range(10):
                try:
                    r = [{"t": float(e[0]), "s": -float(e[1]), "f": str(filepath).split(".")[-1]} for e in (line.strip().split() for line in filepath.open())]
                    if not r:   # pending
                        r = [{"t": 0, "s": 0}]
                    return r
                except ValueError as err:
                    pass        # file is being written at the moment, try again later
                    module_logger.info('(ignored) cannot process {}: {}'.format(filepath.name, err))
                time_m.sleep(3)
            raise RuntimeError("Cannot process {}".format(filepath))

        def time_score_from_log(files):
            return min((load_log_file(filepath)[-1] for filepath in files), key=operator.itemgetter("s"))

        completed = [run_id for run_id in state["raxml"]["run_ids"] if Path(state["raxml"]["output_dir"], "RAxML_bestTree." + run_id).exists()]
        if completed:
            best_completed = time_score_from_log(Path(state["raxml"]["output_dir"], "RAxML_log." + run_id) for run_id in completed)
            # module_logger.info('completed: {} best: {}'.format(len(completed), best_completed))
            running_logs = [f for f in (Path(state["raxml"]["output_dir"], "RAxML_log." + run_id) for run_id in state["raxml"]["run_ids"] if run_id not in completed) if f.exists()]
            data = {int(str(f).split(".")[-1]): load_log_file(f) for f in running_logs}
            scores_for_longer_worse_than_best_completed = {k: v[-1]["s"] for k, v in data.items() if v[-1]["t"] > best_completed["t"] and v[-1]["s"] > best_completed["s"]}
            by_score = sorted(scores_for_longer_worse_than_best_completed, key=lambda e: scores_for_longer_worse_than_best_completed[e])
            n_to_kill = int(len(by_score) * self.config["raxml_kill_rate"])
            if n_to_kill > 0:
                to_kill = by_score[-n_to_kill:]
                module_logger.info('completed: {} best: {} worse_than_best_completed: {} to kill: {}'.format(len(completed), best_completed, by_score, to_kill))
                job = htcondor.Job(clusters=state["raxml"]["cluster"], condor_log=state["raxml"]["condor_log"])
                job.kill_tasks(to_kill)
                run_id_to_del = [ri for ri in state["raxml"]["run_ids"] if int(ri.split(".")[-1]) in to_kill]
                # module_logger.info('run_id_to_del {}'.format(run_id_to_del))
                for ri in run_id_to_del:
                    state["raxml"]["run_ids"].remove(ri)
                # module_logger.info('To kill {}: {} run_ids left: {}'.format(n_to_kill, to_kill, state["raxml"]["run_ids"]))
                # module_logger.info('To kill {}: {}'.format(n_to_kill, to_kill))
            # else:
            #     module_logger.info('Nothing to kill')

    def make_results(self, state):
        raxml_results = RaxmlResults(config=self.config, state=state).read()
        raxml_results.make_txt(Path(state["working_dir"], "result.raxml.txt"))
        raxml_results.make_json(Path(state["working_dir"], "result.raxml.json"))
        make_r_score_vs_time(target_dir=state["working_dir"], source_dir=state["raxml"]["output_dir"], results=raxml_results)
        return raxml_results

# ----------------------------------------------------------------------

class RaxmlResult (maker_base.Result):

    sInfoBestScore = re.compile(r"Final GAMMA-based Score of best tree -([\d\.]+)", re.I)
    sInfoExecutionTime = re.compile(r"Overall execution time: ([\d\.]+) secs ", re.I)

    def __init__(self, best_tree):
        super().__init__()
        self.read(best_tree)

    def read(self, best_tree):
        self.tree = best_tree
        self.run_id = ".".join(best_tree.parts[-1].split(".")[1:])
        info_data = best_tree.parent.joinpath("RAxML_info." + self.run_id).open().read()
        m_score = cls.sInfoBestScore.search(info_data)
        if m_score:
            self.best_score = float(m_score.group(1))
        else:
            raise ValueError("Raxml: cannot extract best score from " + str(Path(output_dir, "RAxML_info." + self.run_id)))
        m_time = cls.sInfoExecutionTime.search(info_data)
        if m_time:
            self.time = float(m_time.group(1))
        else:
            self.time = None
        log_data = best_tree.parent.joinpath("RAxML_log." + self.run_id).open().readlines()
        self.start_scores = [- float(log_data[0].split()[1]), - float(log_data[-1].split()[1])]

    def tabbed_report(self):
        return "{:10.4f} {:>8s} {:10.4f} {:10.4f} {}".format(self.score, self.time_str(self.time), self.start_scores[0], self.start_scores[1], str(self.tree))

# ----------------------------------------------------------------------

class RaxmlResults (maker_base.Results):

    # def __init__(self, results, overall_time, submitted_tasks, survived_tasks):
    #     super().__init__(results=results, overall_time=overall_time, submitted_tasks=submitted_tasks, survived_tasks=survived_tasks)

    def max_start_score(self):
        max_e_all = max(self.results, key=lambda e: max(e.score, *e.start_scores))
        return max(max_e_all.score, *max_e_all.start_scores)

    def tabbed_report_header(cls):
        return "{:^10s} {:^8s} {:^10s} {:^10s} {}".format("score", "time", "startscore", "endscore", "tree")

    def read(self):
        self.results = sorted((RaxmlResult(best_tree) for best_tree in Path(self.state["raxml"]["output_dir"]).glob("RAxML_bestTree.*")), key=operator.attrgetter("score"))
        self.longest_time = max(self.results, key=operator.attrgetter("time")).time if self.results else 0
        self.overall_time = self.state["raxml"]["overall_time"]
        # self.submitted_tasks = submitted_tasks
        # self.survived_tasks = survived_tasks
        return self

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
