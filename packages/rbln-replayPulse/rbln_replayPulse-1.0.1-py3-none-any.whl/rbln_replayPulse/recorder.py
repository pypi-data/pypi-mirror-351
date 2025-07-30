import subprocess
import time
import json
import re
import pandas as pd
from matplotlib import pyplot as plt


class ReplayPulseRecorder:
    def __init__(self, conf, rbln_list):
        self.conf = conf
        self.rbln_list = rbln_list
        self.cmd_list = []
        self.info = []

    def make_cmd(self, rbln):
        self.cmd_list = [
            ['sudo', 'rbln', 'pvt', '-d', str(rbln)],
            ['sudo', 'rbln', 'pwr', '-d', str(rbln)],
            ['sudo', 'rbln-stat', '-j', '-d', str(rbln)]]

    def _run(self, record_list):
        pvt = subprocess.run(self.cmd_list[0], capture_output=True, text=True)
        pvt_output = pvt.stdout.split('\n')

        pwr = subprocess.run(self.cmd_list[1], capture_output=True, text=True)
        pwr_output = pwr.stdout
        pwr_info = re.split(r'[/,:]', pwr_output.split('\n')[0])

        stat = subprocess.run(self.cmd_list[2], capture_output=True, text=True)
        stat_output = json.loads(stat.stdout.strip())

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        record_list.append({
            "timestamp": timestamp,
            "PVT_PEAK": pvt_output[5].split('|')[1].strip()[:-3],
            "PVT_AVG": pvt_output[6].split('|')[1].strip()[:-3],
            "INPUT_BUS_V": int(pwr_info[1][:-3]),
            "INPUT_BUS_C": int(pwr_info[2][:-3]),
            "INPUT_BUS_P": int(pwr_info[3][:-3]),
            "PCIe_link_speed": float(stat_output['devices'][0]['pci']['link_speed'][:-4]),
            "PCIe_link_width": int(stat_output['devices'][0]['pci']['link_width']),
            "Utilization": float(stat_output['devices'][0]['util'])
        })

    def run(self, is_finished, record_list):
        while not is_finished.value:
            self._run(record_list)
            time.sleep(1)

        for _ in range(10):
            self._run(record_list)
            time.sleep(1)

    def save_chip_info(self, gddr_dict):
        for rbln in self.rbln_list:
            chip_info = subprocess.run(
                f"sudo rbln chip_info -d {rbln}",
                check=True,
                shell=True,
                capture_output=True
            )
            chip_info_list = chip_info.stdout.decode('utf-8').split('\n')
            ver_info = subprocess.run(
                "sudo rbln ver",
                check=True,
                capture_output=True,
                shell=True
            )
            ver_list = ver_info.stdout.decode('utf-8').split('\n')
            ber = subprocess.run(
                f"sudo rbln gddr -b -d {rbln}",
                shell=True,
                check=True,
                capture_output=True
            )
            gddr_dict[rbln] = ber.stdout.decode('utf-8')

            self.info.append({
                'RBLN#': rbln,
                'Chip_info': chip_info_list[0].split(':')[1].strip(),
                'SoC_info': chip_info_list[4].split(':')[1].strip(),
                'Board_ver': chip_info_list[5].split(':')[1].strip(),
                'Board_type': chip_info_list[6].split(':')[1].strip(),
                'Tool_ver': ver_list[0].split(']')[-1].strip(),
                'Host_Driver_ver': ver_list[1].split(']')[-1].strip(),
                'FW_ver': re.split(r'[],,]', ver_list[2])[1].strip(),
                'BER': float(ber.stdout.decode('utf-8').split('\n')[-2].split(',')[0].split('=')[-1])
            })

        self.info = pd.DataFrame(self.info)
        self.info.to_csv(f"{self.conf.result_dir}/info.csv", index=False)

    def draw_report(self, resource_record, output_dict):
        for idx, rbln in enumerate(self.info['RBLN#']):

            fig, axs = plt.subplots(4, 1, figsize=(12, 14), sharex=True)

            # pvt & util
            axs[0].plot(
                resource_record[idx]['timestamp'],
                resource_record[idx]['PVT_AVG'],
                color='b',
                linestyle=':',
                label='PVT_AVG'
            )
            axs[0].plot(
                resource_record[idx]['timestamp'],
                resource_record[idx]['PVT_PEAK'],
                color='r',
                linestyle=':',
                label='PVT_PEAK'
            )
            twin = axs[0].twinx()
            twin.plot(
                resource_record[idx]['timestamp'],
                resource_record[idx]['Utilization'],
                linestyle='-.',
                color='g',
                alpha=0.2
            )
            twin.fill_between(
                resource_record[idx]['timestamp'],
                resource_record[idx]['Utilization'],
                edgecolor='green',
                facecolor='green',
                alpha=0.1,
                label='Util'
            )
            twin.set_ylim(0, 110)
            twin.set_ylabel("Util (%)")
            axs[0].set_ylim(20, 80)
            axs[0].set_ylabel("PVT (C)")
            axs[0].grid(True, linestyle=':')
            axs[0].margins(x=0)

            # pwr
            axs[1].plot(
                resource_record[idx]['timestamp'],
                resource_record[idx]['INPUT_BUS_P'],
                color='r',
                label='INPUT_BUS_P'
            )
            axs[1].set_ylabel("INPUT_P (mW)")
            axs[1].tick_params(axis='y', labelcolor='tab:grey')
            axs[1].grid(True, linestyle=':')
            axs[1].margins(x=0)

            # axis 0
            axs[1].set_xlabel("Time (sec)")
            axs[1].tick_params(axis='x', which='both', labelbottom=False)
            fig.legend(loc='upper right', ncol=2, fontsize='small')

            fig.text(
                0.5,
                0.95,
                f"RBLN{rbln} Monitoring Dashboard",
                ha='center',
                weight='bold',
                va='top',
                color='black',
                fontsize=15
            )
            fig.text(
                0.1,
                0.94,
                f"Date : {self.conf.date_str}",
                ha='left',
                va='top',
                fontsize=10,
                color='blue'
            )

            axs[2].axis('off')
            axs[2].margins(x=0)

            # info table
            info_text = [
                ["Chip Info", self.info.iloc[idx]['Chip_info']],
                ["SoC Info", self.info.iloc[idx]['SoC_info']],
                ["Board ver.", self.info.iloc[idx]['Board_ver']],
                ["Board type", self.info.iloc[idx]['Board_type']],
                ["Tool ver.", self.info.iloc[idx]['Tool_ver']],
                ["Host Driver ver.", self.info.iloc[idx]['Host_Driver_ver']],
                ["FW ver.", self.info.iloc[idx]['FW_ver']],
                ["PCIe speed", resource_record[idx].iloc[-1]['PCIe_link_speed']],
                ["PCIe width", resource_record[idx].iloc[-1]['PCIe_link_width']],
                ["BER", self.info.iloc[idx]['BER']]
            ]
            info_table = axs[2].table(cellText=info_text,
                                      colWidths=[0.3, 0.3],
                                      bbox=[0.01, 0.07, 0.4, 0.8],
                                      cellLoc='left',
                                      edges='')

            conf_text = [
                ["Type", self.conf.type],
                ["Workload", self.conf.file.split('/')[-1]],
                ["Test Time", str(self.conf.e)+" (sec)"]
            ]
            conf_table = axs[2].table(cellText=conf_text,
                                      colWidths=[0.3, 0.3],
                                      bbox=[0.55, 0.5, 0.4, 0.3],
                                      cellLoc='left',
                                      edges='')

            for table in [info_table, conf_table]:
                for key, cell in table.get_celld().items():
                    cell.set_fontsize(10)
                    cell.set_linewidth(0.5)

            # ber != 0
            if float(self.info.iloc[idx]['BER']) != 0:
                info_table.get_celld()[(len(info_text)-1, 0)].get_text().set_color('red')
                info_table.get_celld()[(len(info_text)-1, 1)].get_text().set_color('red')

            axs[2].text(
                0.2,
                0.95,
                "Chip Info.",
                fontsize=13,
                weight='bold',
                ha='center',
                transform=axs[2].transAxes
            )
            axs[2].text(
                0.7,
                0.95,
                "Configuration ",
                fontsize=13,
                weight='bold',
                ha='center',
                transform=axs[2].transAxes
            )

            axs[2].plot(
                [0.5, 0.5],
                [0.25, 0.75],
                linestyle='--',
                color='gray',
                linewidth=1,
                transform=axs[2].transAxes
            )

            # perf
            axs[3].text(
                0.5,
                0.95,
                "Performance",
                fontsize=13,
                weight='bold',
                ha='center',
                transform=axs[3].transAxes
            )
            axs[3].text(
                0.2,
                0.85,
                "[called func]",
                fontsize=12,
                ha='center',
                transform=axs[3].transAxes
            )
            axs[3].text(
                0.7,
                0.85,
                "[waited func]",
                fontsize=12,
                ha='center',
                transform=axs[3].transAxes
            )
            axs[3].plot(
                [0.5, 0.5],
                [0.25, 0.75],
                linestyle='--',
                color='gray',
                linewidth=1,
                transform=axs[3].transAxes
            )

            axs[3].axis('off')
            axs[3].margins(x=0)

            if self.conf.type == "replay":
                called_log = output_dict[rbln].split('\n')[-3].split(' ')
                waited_log = output_dict[rbln].split('\n')[-2].split(' ')
            else:
                called_log = output_dict[0].split('\n')[-3].split(' ')
                waited_log = output_dict[0].split('\n')[-2].split(' ')

            called_txt = [
                ["Average(us)", called_log[5]],
                ["Total(us)", called_log[7]],
                ["Count", called_log[9]],
                ["MIN(us)", called_log[11]],
                ["MAX(us)", called_log[13][:-1]]
            ]
            waited_txt = [
                ["Average(us)", waited_log[5]],
                ["Total(us)", waited_log[7]],
                ["Count", waited_log[9]],
                ["MIN(us)", waited_log[11]],
                ["MAX(us)", waited_log[13][:-1]]
            ]

            called_table = axs[3].table(cellText=called_txt,
                                        colWidths=[0.3, 0.3],
                                        bbox=[0.05, 0.25, 0.4, 0.5],
                                        cellLoc='left',
                                        edges='')

            waited_table = axs[3].table(cellText=waited_txt,
                                        colWidths=[0.3, 0.3],
                                        bbox=[0.55, 0.25, 0.4, 0.5],
                                        cellLoc='left',
                                        edges='')

            for table in [called_table, waited_table]:
                for key, cell in table.get_celld().items():
                    cell.set_fontsize(10)
                    cell.set_linewidth(1)

            plt.subplots_adjust(bottom=0.02)

            fig.savefig(f'{self.conf.result_dir}/RBLN{rbln}_dashboard.png')

    def make_report(self, output_dict):
        resource_record = []
        for rbln in self.info['RBLN#']:
            df = pd.read_csv(f"{self.conf.result_dir}/resource_rbln{rbln}.csv")
            resource_record.append(df)

        self.draw_report(resource_record, output_dict)
