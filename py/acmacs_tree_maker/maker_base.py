# -*- Python -*-
# license
# license.
# ======================================================================

import copy, datetime, random
import logging; module_logger = logging.getLogger(__name__)
from pathlib import Path
from acmacs_base import json as json_m

# ----------------------------------------------------------------------

class MakerBase:

    def __init__(self, config):
        self.config = config
        self.random_gen = random.SystemRandom()

    def random_seed(self):
        return self.random_gen.randint(1, 0xFFFFFFF)   # note max for garli is 0x7ffffffe

# ----------------------------------------------------------------------

class Result:

    def __repr__(self):
        return str(vars(self))

    def json(self):
        return vars(self)

    @classmethod
    def time_str(cls, time):
        if time is not None:
            s = str(datetime.timedelta(seconds=time))
        else:
            s = ""
        try:
            return s[:s.index('.')]
        except:
            return s

    @classmethod
    def from_dict(cls, data):
        r = cls(best_tree=None)
        for k, v in data.items():
            setattr(r, k, v)
        return r

# ----------------------------------------------------------------------

class Results:

    def __init__(self, config, state):
        self.config = config
        self.state = state

    def recompute(self):
        self.results.sort(key=operator.attrgetter("score"))
        self.longest_time = max(self.results, key=operator.attrgetter("time")).time

    def longest_time_str(self):
        return Result.time_str(self.longest_time)

    def best_tree(self):
        return self.results[0].tree

    def report_best(self):
        return "{} {} {}".format(self.results[0].score, self.longest_time_str(), self.best_tree())

    def make_txt(self, filepath :Path):
        with filepath.open("w") as f:
            f.write("Longest time:    " + self.longest_time_str()+ "\n")
            if self.overall_time:
                f.write("Overall time:    " + Result.time_str(self.overall_time)+ "\n")
            if self.submitted_tasks:
                f.write("Submitted tasks: " + str(self.submitted_tasks) + "\n")
            if getattr(self, "survived_tasks", None) and self.survived_tasks != self.submitted_tasks:
                f.write("Survived tasks:  " + str(self.survived_tasks) + "\n")
            f.write("\n")
            f.write(self.tabbed_report_header()+ "\n")
            f.write("\n".join(rr.tabbed_report() for rr in self.results) + "\n")

    def make_json(self, filepath :Path):
        data = copy.copy(vars(self))
        data.pop("config", None)
        data.pop("state", None)
        data["results"] = [e.json() for e in data["results"]]
        json_m.write_json(filepath, data)

    @classmethod
    def from_json(cls, config, state, filepath :Path):
        r = cls(config, state)
        data = json_m.read_json(filepath)
        for k, v in data.items():
            setattr(r, k, v)
        if isinstance(r.results[0], dict):
            r.results = [r.result_class().from_dict(result) for result in r.results]
        return r

# ----------------------------------------------------------------------


# ======================================================================
### Local Variables:
### eval: (if (fboundp 'eu-rename-buffer) (eu-rename-buffer))
### End:
