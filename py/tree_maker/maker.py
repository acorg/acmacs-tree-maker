# -*- Python -*-
# license
# license.
# ======================================================================

import sys, traceback
import logging; module_logger = logging.getLogger(__name__)
from pathlib import Path
from . import config as config_m, email
from acmacs_base import json as json_m, files

# ----------------------------------------------------------------------

def step(args):
    config = config_m.load(Path(args.working_dir, args.config_file_name))
    state_filename = Path(args.working_dir, "state.json")
    if state_filename.exists():
        state = json_m.read_json(state_filename)
    else:
        state = {
            "state": "init",
            "working_dir": str(Path(args.working_dir).resolve())
            }
        json_m.write_json(path=state_filename, data=state, indent=2, compact=True)
    new_state = create_runner(config=config, state=state).step().state
    json_m.write_json(path=state_filename, data=new_state, indent=2, compact=True)

# ----------------------------------------------------------------------

def wait(args):
    config = config_m.load(Path(args.working_dir, args.config_file_name))
    state_filename = Path(args.working_dir, "state.json")
    if state_filename.exists():
        state = json_m.read_json(state_filename)
    else:
        state = {
            "state": "init",
            "working_dir": str(Path(args.working_dir).resolve())
            }
        json_m.write_json(path=state_filename, data=state, indent=2, compact=True)
    runner = create_runner(config=config, state=state)
    try:
        while state["state"] != "completed":
            runner.step()
            json_m.write_json(path=state_filename, data=state, indent=2, compact=True)
        if args.email and config.get("email"):
            email.send(to=config["email"], subject="{} completed in {}".format(sys.argv[0], args.working_dir), body="{} completed in\n{}".format(sys.argv[0], args.working_dir))
    except Exception as err:
        if args.email and config.get("email"):
            email.send(to=config["email"], subject="{} FAILED in {}".format(sys.argv[0], args.working_dir), body="{} FAILED in\n{}\n\n{}\n\n{}".format(sys.argv[0], args.working_dir, err, traceback.format_exc()))
        raise

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

    def on_state_init(self):
        # get outgroup from fasta
        self.state["outgroup"] = open(self.config["source"]).readline().strip()[1:]

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
        super().on_state_init()
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
        from .garli import GarliResults
        garli_results = GarliResults.from_json(config=self.config, state=self.state, filepath=Path(self.state["working_dir"], "result.garli.json"))
        r_best = vars(garli_results.results[0])
        r_best["overall_time"] = overall_time
        r_best["overall_time_s"] = overall_time_s
        json_m.write_json(Path(self.state["working_dir"], "result.best.json"), r_best, indent=2, compact=False)

        with Path(self.state["working_dir"], "result.all.txt").open("w") as f:
            f.write("Overall time: " + overall_time_s + "\n")
            f.write("GARLI score : " + str(r_best["score"]) + "\n")
            f.write("Tree        : " + str(r_best["tree"]) + "\n")

        # from .raxml import RaxmlResults
        # raxml_results = RaxmlResults.from_json(config=self.config, state=self.state, filepath=Path(self.state["working_dir"], "result.raxml.json"))
        # results = {
        #     " total": {
        #         "longest_time": longest_time,
        #         "longest_time_s": longest_time_s,
        #         "overall_time": overall_time,
        #         "overall_time_s": overall_time_s,
        #         "tree": str(garli_results.results[0].tree),
        #         "garli_score": garli_results.results[0].score,
        #         },
        #     "garli": [vars(r) for r in garli_results.results],
        #     "raxml": [r if isinstance(r, dict) else vars(r) for r in raxml_results.results],
        #     }
        # json_m.write_json(Path(self.state["working_dir"], "result.all.json"), results, indent=2, compact=True)

        # convert best tree from newick to json
        import tree_newick_to_json
        tree = tree_newick_to_json.Tree()
        tree_newick_to_json.import_newick(open(r_best["tree"]).read(), tree)
        j = tree_newick_to_json.json(tree)
        files.write_binary(Path(self.state["working_dir"], "tree.json.xz"), j)

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
