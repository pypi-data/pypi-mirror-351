from dataclasses import dataclass, field
import datetime
import yaml
import re


@dataclass
class FieldReporterTelegramDestinationConfig:
    api_token: str
    chat_id: str


@dataclass
class FieldReporterScheduleConfig:
    at_times: list = field(default_factory=list)
    at_interval: float = None


@dataclass
class FieldReporterConfig:
    destinations: list
    conditions: list
    schedule: FieldReporterScheduleConfig


@dataclass
class FieldReporterDiskSpaceConditionConfig:
    disks: list = field(default_factory=list)
    threshold_gb: float = 10


@dataclass
class FieldReporterPathsExistConditionConfig:
    pattern: str
    created_since: int = None
    minimum_count: int = 1

@dataclass
class FieldReporterUptimeConditionConfig:
    minimum_uptime: int = None
    maximum_uptime: int = None

def load_config(file_path: str):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)

    destinations = []
    for destination in config.get('destinations', []):
        if destination["type"] == "telegram":
            destination = FieldReporterTelegramDestinationConfig(api_token=destination["api_token"],
                                                                 chat_id=destination["chat_id"])
        destinations.append(destination)

    schedule = FieldReporterScheduleConfig()
    schedule_config = config.get('schedule', {})
    at_times = schedule_config.get('at_times', [])
    for at_time in at_times:
        pattern = r'^(\d{2}):(\d{2})$'
        match = re.match(pattern, at_time)
        if not match:
            raise ValueError(f"Invalid time format: {at_time}. Expected HH:MM.")
        hour = int(match.group(1))
        minute = int(match.group(2))

        schedule.at_times.append(datetime.time(hour=hour, minute=minute))

    conditions = []
    for condition_type, condition_config in config["conditions"].items():
        if condition_type == "paths_exist":
            condition = FieldReporterPathsExistConditionConfig(pattern=condition_config.get("pattern"),
                                                           created_since=condition_config.get("created_since", None),
                                                           minimum_count=condition_config.get("minimum_count", 1))
            conditions.append(condition)
        elif condition_type == "disk_space":
            threshold = condition_config.get("threshold", 10)
            if threshold.endswith("G"):
                threshold = float(threshold[:-1])
            condition = FieldReporterDiskSpaceConditionConfig(disks=condition_config.get("disks", None),
                                                          threshold_gb=threshold)
            conditions.append(condition)
        elif condition_type == "uptime":
            condition = FieldReporterUptimeConditionConfig(minimum_uptime=condition_config.get("minimum_uptime", None),
                                                      maximum_uptime=condition_config.get("maximum_uptime", None))
            conditions.append(condition)
    config = FieldReporterConfig(destinations=destinations,
                                 conditions=conditions,
                                 schedule=schedule)

    return config
