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

# ----------------------------------------------------------------------

class RaxmlFirst (RunnerBase):
    ""

    def on_state_init(self):
        return self.raxml_submit()

    def raxml_submit(self, submit=True):
        from .raxml import Raxml
        raxml = Raxml(config=self.config)
        raxml.prepare(state=self.state)
        if submit:
            raxml.submit(state=self.state)

# ----------------------------------------------------------------------

class RaxmlSurvivedBestGarli (RaxmlFirst):
    ""

# ----------------------------------------------------------------------

class RaxmlBestGarli (RaxmlFirst):
    ""

# ----------------------------------------------------------------------

class RaxmlAllGarli (RaxmlFirst):
    ""

# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
