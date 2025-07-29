import os
import glob
import time
from ..exceptions import ConditionFailedException
from .model import ConditionReport

class FieldReporterPathsExistCondition:
    def __init__(self, pattern, created_since=None, minimum_count=1):
        self.pattern = pattern
        self.pattern = os.path.expanduser(self.pattern)
        self.created_since = created_since
        self.minimum_count = minimum_count

    def check(self):
        matches = glob.glob(self.pattern)
        if self.created_since is not None:
            cutoff = time.time() - self.created_since
            matches = [m for m in matches if os.path.getctime(m) >= cutoff]
        if len(matches) >= self.minimum_count:
            print(" - Condition met (%s): %s files found" % (self.pattern, len(matches)))
        else:
            raise ConditionFailedException("Not enough files found matching %s (found %d, minimum %d)" % (self.pattern, len(matches), self.minimum_count))
        return ConditionReport("Matching files: %d" % len(matches))
        