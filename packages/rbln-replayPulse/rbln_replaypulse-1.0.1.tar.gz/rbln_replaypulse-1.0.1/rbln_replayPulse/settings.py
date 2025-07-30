import datetime
import argparse
import os
from ast import literal_eval
import subprocess

END = "\033[0m"
BOLD = "\033[1m"
WHITE = "\033[37m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"


# Set up the configuration
class Settings:
    def __init__(self):
        self.rbln_cnt = int(subprocess.run(
            "lspci | grep accelerator | wc -l",
            capture_output=True,
            text=True,
            shell=True
            ).stdout)

        self.group_dict = dict()
        group_info = subprocess.run(
                "cat /sys/class/rebellions/rsd/rsd_group",
                check=True,
                shell=True,
                text=True,
                capture_output=True
            ).stdout.split('\n')[1:-1]
        for info in group_info:
            g_id, _, rbln = info.split(',')
            g_id = int(g_id)
            if g_id not in self.group_dict.keys():
                self.group_dict[g_id] = []
            self.group_dict[g_id].append(int(rbln[4:]))

        self.date = datetime.datetime.now()
        self.date_str = self.date.strftime("%Y/%m/%d %H:%M:%S")
        self.result_dir = f"./results/{self.date.strftime('%Y_%m_%d/%H_%M_%S')[2:]}"
        self.conf = None

    def check_type_value(self, rtype):
        if rtype not in ["replay", "retrace"]:
            raise argparse.ArgumentTypeError(
                f"\n{RED}Invalid execution type '{rtype}'.{END} "
                f"Please choose either {YELLOW}'replay' or 'retrace'{END}."
            )
        return rtype

    def check_file_value(self, path):
        if not os.path.exists(path):
            raise argparse.ArgumentTypeError(
                f"\n{RED}File not found: '{path}'.{END} "
                f"Please check that the file exists at '{path}'."
            )
        return path

    def check_device_value(self, value):
        try:
            value = int(value)
            if value >= self.rbln_cnt or value < 0:
                raise argparse.ArgumentTypeError(
                    f"\n{RED}Invalid device ID '{value}'.{END} "
                    f"Must be {YELLOW}between 0 and {self.rbln_cnt - 1}{END}."
                )
            return value
        except ValueError:
            try:
                value = literal_eval(value)
                if not type(value) is list or not all(type(v) is int for v in value):
                    raise argparse.ArgumentTypeError(
                        f"\n{RED}Invalid device input '{value}'{END}. "
                        f"Allowed values are: {YELLOW}integer, list of integers, or 'all'{END}."
                    )
                if max(value) >= self.rbln_cnt or min(value) < 0:
                    raise argparse.ArgumentTypeError(
                        f"\n{RED}Invalid device ID(s) in list '{value}'{END}. "
                        f"Must be {YELLOW}between 0 and {self.rbln_cnt - 1}{END}."
                    )
                return value
            except (ValueError, SyntaxError):
                if value != "all":
                    raise argparse.ArgumentTypeError(
                        f"\n{RED}Invalid device input '{value}'.{END} "
                        f"Allowed values are: {YELLOW}integer, list of integers, or 'all'{END}."
                    )
                return value

    def check_time_value(self, time):
        try:
            return int(time)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"{RED}Invalid time value '{time}'.{END} "
                f"{YELLOW}Expected integer{END} (e.g., 10, 30, 60)."
            )

    def check_report_value(self, value):
        try:
            value = int(value)
            if value not in [0, 1]:
                raise argparse.ArgumentTypeError(
                    f"{RED}Invalid report value '{value}'.{END} "
                    f"Please choose either {YELLOW}'1(YES)' or '0(NO)'{END}."
                )
            return value
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"{RED}Invalid report value '{value}'.{END} "
                f"Please choose either {YELLOW}'1(YES)' or '0(NO)'{END}."
            )

    def check_group_value(self, value):
        try:
            value = int(value)
            if value not in self.group_dict.keys():
                raise argparse.ArgumentTypeError(
                    f"\n{RED}Invalid group ID '{value}'{END}. "
                    f"Please check that the group ID '{value}' exists."
                )
            return value
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"{RED}Invalid group value '{value}'.{END} "
                f"{YELLOW}Expected integer{END} (e.g., 0, 1, 2)."
            )

    def set_conf(self):
        parser = argparse.ArgumentParser(
            usage=f"{BLUE}%(prog)s{END} {RED}TYPE{END} [-h] {RED}FILE{END} "
            f"{YELLOW}[-d DEVICE] [-e ELAPSED TIME] [-g GROUP ID] [-r REPORT]{END}",
            description=(
                f"{BLUE}{BOLD}RBLN-ReplayPulse{END}\n\n"
                "This tool allows you to replay or retrace previously recorded pulses.\n"
                "You must select the replay type and provide a workload file path."
            ),
            epilog=f"{CYAN}Example:{END} %(prog)s replay workload.bin -d 1 -e 60 -r 1",
            formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument("type",
                            type=self.check_type_value,
                            help=(
                                f"select the replay-pulse execution type "
                                f"{RED}(str; replay|retrace){END}"
                            ),
                            metavar="TYPE")
        parser.add_argument("file",
                            type=self.check_file_value,
                            help=(
                                f"specify the path to the workload file "
                                f"{RED}(str){END}"
                            ),
                            metavar="FILE")
        parser.add_argument("-d",
                            default=0,
                            type=self.check_device_value,
                            help=(
                                f"set the device ID to execute the replay-pulse on "
                                f"{YELLOW}(int|list|'all') (default:0){END}\n"
                                f"{CYAN}=> only for replay{END}"
                            ),
                            metavar="DEVICE")
        parser.add_argument("-e",
                            default=30,
                            type=self.check_time_value,
                            help=(
                                f"execute replay-pulse for the given number of seconds "
                                f"{YELLOW}(int) (default:30){END}"
                            ),
                            metavar="TIME")
        parser.add_argument("-r",
                            default=0,
                            type=self.check_report_value,
                            help=(
                                f"enable or disable report generation "
                                f"{YELLOW}(int; YES(1)|NO(0)) (default:0){END}"
                            ),
                            metavar="REPORT")
        parser.add_argument("-g",
                            default=0,
                            type=self.check_group_value,
                            help=(
                                f"set the group ID to execute the replay-pulse on "
                                f"{YELLOW}(int) (default:0){END}\n"
                                f"{CYAN}=> only for retrace{END}"
                            ),
                            metavar="GROUP")
        self.conf = parser.parse_args()
        self.conf.rbln_cnt = self.rbln_cnt
        self.conf.group_dict = self.group_dict
        self.conf.result_dir = self.result_dir
        self.conf.date_str = self.date_str

        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
