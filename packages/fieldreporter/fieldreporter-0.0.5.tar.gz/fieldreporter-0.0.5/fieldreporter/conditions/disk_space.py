import shutil
from ..exceptions import ConditionFailedException
from .model import ConditionReport

class FieldReporterDiskSpaceCondition:
    def __init__(self, threshold, disks):
        self.threshold = threshold
        self.disks = disks

    def check(self):
        report = "Disk space: "
        free_gb_list = []
        for disk in self.disks:
            usage = shutil.disk_usage(disk)
            free_gb = usage.free / (1024 ** 3)
            free_gb_list.append("%.1fGB" % free_gb)
            if free_gb >= self.threshold:
                print(" - Condition met (%s): %.1fGB free" % (disk, free_gb))
            else:
                raise ConditionFailedException(f"Disk {disk} has only {free_gb:.1f}GB free, below threshold of {self.threshold:.1f}GB.")
        report = report + ", ".join(free_gb_list)
        return ConditionReport(report)