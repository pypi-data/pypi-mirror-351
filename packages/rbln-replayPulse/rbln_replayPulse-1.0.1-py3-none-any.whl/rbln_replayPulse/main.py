#!/usr/bin/env python3

import multiprocessing
import subprocess
import time
from . import settings as st
from . import player as py
from . import recorder as rcd
import pandas as pd


def main():
    setting = st.Settings()
    setting.set_conf()

    p = py.ReplayPulse(setting.conf)
    p.make_cmd()

    subprocess.run("sudo dmesg -c", capture_output=True, check=True, shell=True)

    # shared variable
    is_finished = multiprocessing.Value('b', False)
    is_failed = multiprocessing.Value('b', False)
    manager = multiprocessing.Manager()

    rec = rcd.ReplayPulseRecorder(setting.conf, p.rbln_list)

    resource_record = []
    r_list = []
    for idx, rbln in enumerate(rec.rbln_list):
        rec.make_cmd(rbln)
        resource_record.append(manager.list())
        r_list.append(
            multiprocessing.Process(
                target=rec.run, args=(is_finished, resource_record[idx])
            )
        )
        r_list[-1].start()

    time.sleep(5)

    output_dict = manager.dict()
    p_list = []
    for idx, cmd in enumerate(p.cmd_list):
        p_list.append(
            multiprocessing.Process(
                target=p.run, args=(cmd, is_finished, is_failed, idx, output_dict)
            )
        )
        p_list[-1].start()

    for mp in p_list:
        mp.join()

    for mr in r_list:
        mr.join()

    gddr_dict = dict()
    rec.save_chip_info(gddr_dict)

    if setting.conf.type == "replay":
        with open(f"{setting.result_dir}/output.log", 'a', encoding='utf-8') as f:
            for rbln, output in output_dict.items():
                f.write(f"========================= RBLN{rbln} =========================\n")
                f.write(output)
                f.write('\n')
                f.write(gddr_dict[rbln])
                f.write('\n')
    else:
        with open(f"{setting.result_dir}/output.log", 'a', encoding='utf-8') as f:
            f.write(output_dict[0])
            f.write('\n')
            for rbln, gddr in gddr_dict.items():
                f.write(f"========================= RBLN{rbln} =========================\n")
                f.write(gddr)
                f.write('\n')

    for idx, rbln in enumerate(rec.rbln_list):
        pd.DataFrame(list(
            resource_record[idx]
        )).to_csv(f"{setting.result_dir}/resource_rbln{rbln}.csv", index=False)

    if setting.conf.r == 1 and not is_failed.value:
        rec.make_report(output_dict)

    if is_failed.value:
        dmesg = f"{setting.result_dir}/kernel_log_{setting.conf.file.split('/')[-1][:-4]}.log"
        with open(dmesg, 'a', encoding='utf-8') as f:
            f.write(subprocess.run(
                "sudo dmesg -T",
                capture_output=True,
                text=True,
                shell=True
            ).stdout)

    # reset
    subprocess.run("reset", capture_output=True, text=True, shell=True)
