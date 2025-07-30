import os
from colorama import Fore, Style, init
import re
import datetime
from enum import Enum

class Status(Enum):
    PENDING = "PENDING"
    PREPARING = "PREPARING"
    READY = "READY"
    STARTED = "STARTED"
    STOPPED = "STOPPED"
    PAUSED = "PAUSED"
    UNPAUSED = "UNPAUSED"
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TERMINATED = "TERMINATED"
    DESTROYED = "DESTROYED"
    DEAD = "DEAD"
    REGISTERED = "REGISTERED" ## When registedted in workflow

    UNKNOWN = "UNKNOWN"
    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, value):
        try:
            return cls(value.strip().upper())
        except ValueError:
            return cls.UNKNOWN
class CommandStatus(Enum):
    START = "START"
    STOP = "STOP"
    PAUSE = "PAUSE"
    UNPAUSE = "UNPAUSE"
    DESTROY = "DESTROY"
    RESTART = "RESTART"
    CREATE = "CREATE"
    DELETE = "DELETE"
    UPDATE = "UPDATE"
    REMOVE = "REMOVE"
    TERMINATE = "TERMINATE"

    UNKNOWN = "UNKNOWN"
    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, value):
        try:
            return cls(value.strip().upper())
        except ValueError:
            return cls.UNKNOWN
class FLowRegisteryStatus(Enum):
    PUBLISHED = "PUBLISHED"
    DRAFT = "DRAFT"
    STAGED = "STAGED"
    TEST   = "TEST"

    UNKNOWN = "UNKNOWN"

    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, value):
        try:
            return cls(value.strip().upper())
        except ValueError:
            return cls.UNKNOWN
     

def print_table(data_list, headers, max_width=30):  # Increase max_width to 30 or another suitable value
    if not data_list or not headers:
        print("No data to display")
        return

    col_widths = {header: min(max(len(header), max(len(str(row.get(header, "")).replace('\n', ' ')) for row in data_list)), max_width) for header in headers}

    row_format = " | ".join([f"{{:<{col_widths[header]}.{col_widths[header]}}}" for header in headers])

    print("\n" + row_format.format(*headers))
    print("-+-".join(["-" * col_widths[header] for header in headers]))

    for row in data_list:
        row_data = [str(row.get(header, "")).replace('\n', ' ').replace('[', '').replace(']', '').replace("'", "")[:col_widths[header]] for header in headers]
        print(row_format.format(*row_data))


def log_viewer(logs: dict, new_lines: bool = False):
    init(autoreset=True)

    # Group logs by container id
    logs_by_container = {}
    for entry in logs:
        cid = entry.get("container")
        logs_by_container.setdefault(cid, []).append(entry)

    # For each container, print a table with the container id as header,
    # then print the date and message (splitting multi-line messages)
    for container_id, entries in logs_by_container.items():
        if not new_lines:
            print("\n" + "=" * 40)
            print(f"Container: {container_id}")
            print("=" * 40)
            # Print table header
            print(f"{'Date':<20} {'Message'}")
        for log in entries:
            # format date from milliseconds
            log_date = (
                datetime.datetime.fromtimestamp(log["date"] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                if log.get("date") else ""
            )
            # Determine line color based on severity
            severity = log.get("severity", 0)
            if severity <= 3:
                color = Fore.GREEN
            elif severity == 6:
                color = Fore.RED
            else:
                color = Fore.WHITE
                
            # Split message into lines (each gets its own date)
            message_lines = log.get("message", "").splitlines()
            # Remove leading log date from each message line if present
            cleaned_lines = []
            for line in message_lines:
                pattern = r'^(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})\s*'
                match = re.match(pattern, line)
                if match:
                    # try:
                    #     match_dt = datetime.datetime.strptime(match.group(1), "%Y/%m/%d %H:%M:%S")
                    #     log_date_dt = datetime.datetime.strptime(log_date, "%Y-%m-%d %H:%M:%S")
                    #     print(f"match_dt: {match_dt}, log_date_dt: {log_date_dt}")
                    #     if match_dt == log_date_dt:
                    #          line = line[len(match.group(0)):]
                    # except ValueError:
                    #     pass  
                    line = line[len(match.group(0)):]
                cleaned_lines.append(line)
            message_lines = cleaned_lines
            for line in message_lines:
                print(f"{color}{log_date:<20} {line}{Style.RESET_ALL}")
