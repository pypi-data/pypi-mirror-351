import psutil
import time

from .model import ConditionReport
from ..exceptions import ConditionFailedException

class FieldReporterUptimeCondition:
    def __init__(self, minimum_uptime=None, maximum_uptime=None):
        self.minimum_uptime = int(minimum_uptime) if minimum_uptime is not None else None
        self.maximum_uptime = int(maximum_uptime) if maximum_uptime is not None else None

    def check(self):
        boot_time = psutil.boot_time()
        uptime_seconds = int(time.time() - boot_time)

        if self.minimum_uptime is not None:
            if uptime_seconds >= self.minimum_uptime:
                print(" - Condition met (uptime %d >= minimum %d)" % (uptime_seconds, self.minimum_uptime))
            else:
                raise ConditionFailedException("Condition failed (uptime %d < minimum %d)" % (uptime_seconds, self.minimum_uptime))
            
        if self.maximum_uptime is not None:
            if uptime_seconds <= self.maximum_uptime:
                print(" - Condition met (uptime %d <= maximum %d)" % (uptime_seconds, self.maximum_uptime))
            else:
                raise ConditionFailedException("Condition failed (uptime %d > maximum_uptime %d)" % (uptime_seconds, self.maximum_uptime))
        return ConditionReport("Uptime: %dh %02dm %02ds" % ((uptime_seconds // 3600),
                                                           (uptime_seconds // 60) % 60,
                                                           (uptime_seconds % 60)))