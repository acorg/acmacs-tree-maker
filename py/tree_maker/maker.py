# -*- Python -*-
# license
# license.
# ======================================================================

import logging; module_logger = logging.getLogger(__name__)
from pathlib import Path
from . import config as config_m
from acmacs_base import json

# ----------------------------------------------------------------------

def step(args):
    config = config_m.load(Path(args.working_dir, args.config_file_name))
    state_filename = Path(args.working_dir, "state.json")
    if state_filename.exists():
        state = json.read_json(state_filename)
    else:
        state = {
            "state": "init",
            "working_dir": str(Path(args.working_dir).resolve())
            }
        json.write_json(path=state_filename, data=state, indent=2, compact=True)
    new_state = create_runner(config=config, state=state).step().state
    json.write_json(path=state_filename, data=new_state, indent=2, compact=True)

# ----------------------------------------------------------------------

def wait(args):
    config = config_m.load(Path(args.working_dir, args.config_file_name))
    state_filename = Path(args.working_dir, "state.json")
    if state_filename.exists():
        state = json.read_json(state_filename)
    else:
        state = {
            "state": "init",
            "working_dir": str(Path(args.working_dir).resolve())
            }
        json.write_json(path=state_filename, data=state, indent=2, compact=True)
    runner = create_runner(config=config, state=state)
    while state["state"] != "completed":
        runner.step()
        json.write_json(path=state_filename, data=state, indent=2, compact=True)

# ----------------------------------------------------------------------

def create_runner(config, state):
    if config["mode"] == "raxml_survived_best_garli":
        runner = RaxmlSurvivedBestGarli(config=config, state=state)
    elif config["mode"] == "raxml_best_garli":
        runner = RaxmlBestGarli(config=config, state=state)
    elif config["mode"] == "raxml_all_garli":
        runner = RaxmlAllGarli(config=config, state=state)
    else:
        raise ValueError("Unsupported mode: " + repr(config["mode"]))
    return runner

# ----------------------------------------------------------------------

class RunnerBase:

    def __init__(self, config, state):
        self.config = config
        self.state = state

    def step(self):
        getattr(self, "on_state_" + self.state["state"])()
        return self

    def on_state_completed(self):
        module_logger.info('Completed')

    def on_state_garli_submitted(self, **kwargs):
        garli = self.get_garli()
        if not self.state["garli"].get("overall_time"):
            garli.wait(state=self.state)
        if self.state["garli"].get("overall_time"):
            garli.make_results(state=self.state)
            self.state["state"] = "garli_done"

    def get_raxml(self):
        from .raxml import Raxml
        return Raxml(config=self.config)

    def get_garli(self):
        from .garli import Garli
        return Garli(config=self.config)

    def raxml_submit(self, submit=True):
        raxml = self.get_raxml()
        raxml.prepare(state=self.state)
        if submit:
            raxml.submit(state=self.state)

    def garli_submit(self, submit=True):
        garli = self.get_garli()
        garli.prepare(state=self.state)
        if submit:
            garli.submit(state=self.state)

# ----------------------------------------------------------------------

class RaxmlGarli (RunnerBase):

    def on_state_init(self):
        return self.raxml_submit()

    def on_state_raxml_done(self, **kwargs):
        self.garli_submit()

    def on_state_garli_done(self, **kwargs):
        self.make_results()
        self.state["state"] = "completed"

    def make_results(self):
        from .maker_base import Result
        overall_time = self.state["raxml"]["overall_time"] + self.state["garli"]["overall_time"]
        overall_time_s = Result.time_str(overall_time)
        module_logger.info('Overall time: ' + overall_time_s)

    # def make_results(cls, raxml_results, garli_results, working_dir, seqdb):
    #     longest_time = raxml_results.longest_time + garli_results.longest_time
    #     longest_time_s = RaxmlResult.time_str(longest_time)
    #     module_logger.info('Longest time: ' + longest_time_s)
    #     if raxml_results.overall_time and garli_results.overall_time:
    #         overall_time = raxml_results.overall_time + garli_results.overall_time
    #         overall_time_s = RaxmlResult.time_str(overall_time)
    #         module_logger.info('Overall time: ' + overall_time_s)
    #     else:
    #         overall_time = None
    #         overall_time_s = ""

    #     r_best = vars(garli_results.results[0])
    #     r_best["longest_time"] = longest_time
    #     r_best["longest_time_s"] = longest_time_s
    #     if overall_time:
    #         r_best["overall_time"] = overall_time
    #     if overall_time_s:
    #         r_best["overall_time_s"] = overall_time_s
    #     json.dumpf(Path(working_dir, "result.best.json"), r_best)

    #     with Path(working_dir, "result.all.txt").open("w") as f:
    #         f.write("Longest time: " + longest_time_s + "\n")
    #         if overall_time_s:
    #             f.write("Overall time: " + overall_time_s + "\n")
    #         f.write("GARLI score : " + str(r_best["score"]) + "\n")
    #         f.write("Tree        : " + str(r_best["tree"]) + "\n")
    #     results = {
    #         " total": {
    #             "longest_time": longest_time,
    #             "longest_time_s": longest_time_s,
    #             "overall_time": overall_time,
    #             "overall_time_s": overall_time_s,
    #             "tree": str(garli_results.results[0].tree),
    #             "garli_score": garli_results.results[0].score,
    #             },
    #         "garli": [vars(r) for r in garli_results.results],
    #         "raxml": [r if isinstance(r, dict) else vars(r) for r in raxml_results.results],
    #         }
    #     json.dumpf(Path(working_dir, "result.all.json"), results)

    #     from .draw_tree import draw_tree
    #     draw_tree(tree_file=r_best["tree"],
    #               seqdb=seqdb,
    #               output_file=Path(working_dir, "tree.pdf"),
    #               title="{{virus_type}} GARLI-score: {} Time: {} ({})".format(r_best["score"], overall_time_s, longest_time_s),
    #               pdf_width=1000, pdf_height=850
    #               )
    #     return results

# ----------------------------------------------------------------------

class RaxmlSurvivedBestGarli (RaxmlGarli):

    def on_state_raxml_submitted(self, **kwargs):
        raxml = self.get_raxml()
        if not self.state["raxml"].get("overall_time"):
            raxml.wait(state=self.state)
        if not self.state["raxml"].get("overall_time"):
            raxml.analyse_logs(state=self.state)
        else:
            raxml.make_results(state=self.state)
            self.state["state"] = "raxml_done"

# ----------------------------------------------------------------------

class RaxmlBestGarli (RaxmlGarli):

    def on_state_raxml_submitted(self, **kwargs):
        raxml = get_raxml()
        if not self.state["raxml"].get("overall_time"):
            raxml.wait(state=self.state)
        if self.state["raxml"].get("overall_time"):
            raxml.make_results(state=self.state)
            self.state["state"] = "raxml_done"

# ----------------------------------------------------------------------

class RaxmlAllGarli (RaxmlGarli):
    ""

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
