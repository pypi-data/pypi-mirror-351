import subprocess
import os


class ReplayPulse:
    def __init__(self, conf):
        self.conf = conf
        self.rbln_list = []
        self.cmd_list = []
        self.env = os.environ.copy()

    def make_cmd(self):
        cmd = []
        if self.conf.type == "replay":
            cmd.append("rblnreplayer")
            cmd.append("--get_perf")
            cmd.append("1")
            cmd.append("-e")
            cmd.append(f"{self.conf.e}")
            cmd.append(f"{self.conf.file}")
            cmd.append("-d")

            if type(self.conf.d) is int:
                self.rbln_list.append(f"{self.conf.d}")
            elif type(self.conf.d) is list:
                self.rbln_list = self.conf.d
            else:
                if self.conf.d == "all":
                    self.rbln_list = range(int(self.conf.rbln_cnt))

            for rbln in self.rbln_list:
                cmd.append(f"{rbln}")
                self.cmd_list.append(list(cmd))
                cmd.pop(-1)

        elif self.conf.type == "retrace":
            self.env["RBLNTHUNK_PERF"] = "1"
            cmd.append("rblntrace")
            cmd.append(f"{self.conf.type}")
            cmd.append("-e")
            cmd.append(f"{self.conf.e}")
            cmd.append(f"{self.conf.file}")
            self.cmd_list.append(cmd)
            self.rbln_list = self.conf.group_dict[self.conf.g]

    def run(self, cmd, is_finished, is_failed, idx, output_dict):
        player = subprocess.run(cmd, capture_output=True, text=True, env=self.env)
        with is_finished.get_lock():
            is_finished.value = True

        output_dict[self.rbln_list[idx]] = player.stdout

        if not player.stdout.split('\n')[-4].split(' ')[1].startswith('PASSED'):
            is_failed.value = True
