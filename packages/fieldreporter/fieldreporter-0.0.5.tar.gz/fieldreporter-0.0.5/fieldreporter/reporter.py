from apscheduler.schedulers.background import BackgroundScheduler
from .config import load_config
from .config import FieldReporterTelegramDestinationConfig
from .config import FieldReporterDiskSpaceConditionConfig, FieldReporterPathsExistConditionConfig, FieldReporterUptimeConditionConfig
from .destinations import TelegramDestination
from .conditions import FieldReporterDiskSpaceCondition, FieldReporterPathsExistCondition, FieldReporterUptimeCondition
from .exceptions import ConditionFailedException
import time
import socket

class FieldReporter:
    def __init__(self,
                 config_path):
        self.destinations = []
        self.conditions = []
        self.schedule = []
        config = load_config(config_path)
        for destination_config in config.destinations:
            if isinstance(destination_config, FieldReporterTelegramDestinationConfig):
                self.destinations.append(TelegramDestination(destination_config.api_token,
                                                             destination_config.chat_id))
        for condition_config in config.conditions:
            if isinstance(condition_config, FieldReporterDiskSpaceConditionConfig):
                self.conditions.append(FieldReporterDiskSpaceCondition(threshold=condition_config.threshold_gb,
                                                                   disks=condition_config.disks))
            elif isinstance(condition_config, FieldReporterPathsExistConditionConfig):
                self.conditions.append(FieldReporterPathsExistCondition(pattern=condition_config.pattern,
                                                                    created_since=condition_config.created_since,
                                                                    minimum_count=condition_config.minimum_count))
            elif isinstance(condition_config, FieldReporterUptimeConditionConfig):
                self.conditions.append(FieldReporterUptimeCondition(minimum_uptime=condition_config.minimum_uptime,
                                                                maximum_uptime=condition_config.maximum_uptime))
        self.schedule = config.schedule
        self.hostname = socket.gethostname()

    def run(self):
        scheduler = BackgroundScheduler()
        scheduler.start()
        
        for at_time in self.schedule.at_times:
            scheduler.add_job(self.check_all, 'cron', hour=at_time.hour, minute=at_time.minute)

        at_times_str = ", ".join([f"{at_time.hour:02}:{at_time.minute:02}" for at_time in self.schedule.at_times])
        print("FieldReporter: Scheduler started. Waiting for scheduled checks (at times: %s)..." % at_times_str)

        while True:
            time.sleep(1)
    
    def message(self, message):
        for destination in self.destinations:
            destination.send("%s (%s)" % (message, self.hostname))

    def error(self, message):
        for destination in self.destinations:
            destination.send("ERROR: %s (%s)" % (message, self.hostname))

    def warning(self, message):
        for destination in self.destinations:
            destination.send("WARNING: %s (%s)" % (message, self.hostname))

    def check_all(self):
        print("FieldReporter: Checking all conditions...")
        reports = []
        success = True
        for condition in self.conditions:
            try:
                report = condition.check()
                reports.append(report)
            except ConditionFailedException as e:
                print(f" - Condition failed: {e}")
                self.error(str(e))
                success = False

        if success:
            message = "FieldReporter: All conditions succeeded.\n"
            for report in reports:
                message += " - %s\n" % str(report)
            self.message(message)