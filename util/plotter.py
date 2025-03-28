import sys
import os
from .os_operate import dir_check, file_list
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams
import matplotx, scienceplots


class Workstation:
    """define a electrochemical workstation"""
    __supported_workstation_type = ('kst', 'ch')
    def __init__(self, workstation_type):
        if workstation_type in self.__class__.__supported_workstation_type:
            self.workstation_type = workstation_type
        else:
            raise ValueError(f'workstation {workstation_type} is not supported current')
        self.storage_data_dict = {}


class Data(Workstation):
    """define how to split and normalize data"""
    __supported_plot_type = ('cv', 'ca')
    __cut_line_number = {'kst': 25, 'ch': 13}
    def __init__(self, workstation_type, plot_type):
        super().__init__(workstation_type)
        if plot_type in self.__class__.__supported_plot_type:
            self.plot_type = plot_type
        else:
            raise ValueError("plot type is not supported current")


    def check_path(self, path):
        if os.path.isdir(path):
            return os.listdir(path)
        elif os.path.isfile(path):
            return [path]
        else:
            path_list = file_list(path)
            return path_list


    def write_data(self, data_list, dirname, comment=None, one_file=False):
        if one_file:
            if not isinstance(data_list, np.ndarray):
                data_list_array = np.array(data_list, dtype=float)
                np.savetxt(f"{dirname}", data_list_array, delimiter='\t', header=comment)
            else:
                np.savetxt(f"{dirname}", data_list, delimiter='\t', header=comment)
        else:
            dir_check(dirname, delete=False)
            for i in range(len(data_list)):
                if not isinstance(data_list[i], np.ndarray):
                    data_list_array = np.array(data_list[i], dtype=float)
                    np.savetxt(f"{dirname}/cycle_{i}.dat", data_list_array, delimiter='\t', header=comment)
                else:
                    np.savetxt(f"{dirname}/cycle_{i}.dat", data_list[i], delimiter='\t', header=comment)


    def file_name_parse(self, file_name):
        file_name = file_name.split('.')

        file_prefix = '.'.join(file_name[:-1])
        file_suffix = file_name[-1]

        splited_prefix = file_prefix.split('_')
        if len(splited_prefix) < 2:
            ph = None
            area = None
            return file_prefix, ph, area
        ph_part = splited_prefix[-2].split('-')
        area_part = splited_prefix[-1].split('-')
        if (ph_part[0] != 'ph' and ph_part[0] != 'pH') or (area_part[0] != 'area' and area_part[0] != 'A' and area_part[0] != 'Area'):
            ph = None
            area = None
        else:
            ph = float(ph_part[-1])
            area = float(area_part[-1])

        return file_prefix, ph, area


    def split_data(self, input_path, cut=None):
        filename_list = self.check_path(input_path)
        for filename in filename_list:
            if os.path.isfile(filename):
                filename = filename
            else:
                filename = f"{input_path}/{filename}"
            if os.path.isfile(filename):
                file_prefix, ph, area = self.file_name_parse(filename)
                self.storage_data_dict[file_prefix] = ph, area
                dir_name = file_prefix
                dir_check(dir_name)
                if self.workstation_type == 'kst':
                    if cut is None:
                        cut = self.__cut_line_number['kst']

                    with open(filename, 'r', encoding='cp1252') as f:
                        data = f.read()

                    line_data = data.splitlines()
                    line_data = line_data[cut:]

                    data_list = []
                    data_list_list = []
                    for line in line_data:
                        data = line.split()
                        if len(data) == 3:
                            data_list.append(data)
                            continue
                        if len(data) == 5:
                            data_list_list.append(data_list)
                            data_list = []
                            data_list.append(data[:3])
                            continue
                    data_list_list.append(data_list)
                    self.write_data(data_list_list, f"{dir_name}/raw_data", comment="E(V)\ti(A/cm2)\tT(s)\n")


                if self.workstation_type == 'ch':
                    if cut is None:
                        cut = self.__cut_line_number['ch']
                    with open(filename, 'r', encoding='cp1252') as f:
                        data = f.read()
                    if self.plot_type == 'ca':
                        separator = 'Step'
                    if self.plot_type == 'cv':
                        separator = 'Segment'

                    line_data = data.splitlines()
                    line_data = line_data[cut:]

                    data_list = []
                    data_list_list = []
                    for line in line_data:
                        data = line.split(',')
                        if data[0] == '':
                            continue
                        if data[0][:len(separator)] == separator:
                            data_list_list.append(data_list)
                            data_list = []
                            continue
                        data_list.append(data)
                    data_list_list.append(data_list)
                    self.write_data(data_list_list, f"{dir_name}/raw_data", comment="")
                #print(f"\033[91msplit\033[0m of \033[34m{filename}\033[0m is done".replace('\\','/'))
                print(f"split of {filename} is done".replace('\\','/'))


    def normalize_data(self, input_area=None, input_pH=None, reference='AgCl'):
        reference_dict = {'AgCl': 0.197, 'SCE': 0.241, 'CSE': 0.314, }
        #for folder in os.listdir(input_path):
        for folder in self.storage_data_dict.keys():
            if os.path.isdir(folder):
                raw_data_folder = folder + '/' + 'raw_data'
                normalized_data_folder = folder + '/' + 'normalized_data'
                dir_check(normalized_data_folder, delete=False)
                for filename in os.listdir(raw_data_folder):
                    raw_filename_path = raw_data_folder + '/' + filename
                    normalized_filename_path = normalized_data_folder + '/' + filename
                    pH, area = self.storage_data_dict[folder]
                    if pH is None:
                        pH = input_pH
                        if input_pH is None:
                            raise ValueError("please give a pH")
                    if area is None:
                        area = input_area
                        if input_area is None:
                            raise ValueError("please give a area")
                    data = np.loadtxt(raw_filename_path)
                    if data.size == 0:
                        continue
                    if self.plot_type == 'cv':
                        data[:, 0] = data[:, 0] + reference_dict[reference] + 0.059*pH
                        data[:, 1] = (data[:, 1]*1000) / area
                        self.write_data(data[:, 0:2], normalized_filename_path, comment="E(V .Vs. RHE)\ti(mA/cm2)\n", one_file=True)
                    if self.plot_type == 'ca':
                        if self.workstation_type == 'kst':
                            data[:, 2] = data[:, 2] / 3600
                            data[:, 1] = (data[:, 1]*1000) / area
                            self.write_data(data[:, -1:-3:-1], normalized_filename_path, comment="T(h)\ti(mA/cm2)\n", one_file=True)
                        if self.workstation_type == 'ch':
                            x = data[:, 0] / 3600
                            y = (data[:, 1]*1000) / area
                            self.write_data(data[:, 0:2], normalized_filename_path, comment="T(h)\ti(mA/cm2)\n", one_file=True)
                    print(f"normalize of {folder} is done")
                    print(f"pH={pH}\narea={area}\n")


class Plot(Data):

    def __init__(self, workstation_type, plot_type, plot_style, dpi=300, color=False, latex=False, half=True, half_check=0.6):
        self.science_style_list = ('ieee', 'nature')
        self.matplotx_style_list = dir(matplotx.styles)

        super().__init__(workstation_type, plot_type)
        rcParams['figure.dpi'] = dpi
        if plot_style in self.science_style_list:
            self.plot_style = ['science', plot_style]
            if not latex:
                self.plot_style.append('no-latex')
            if color:
                self.plot_style.append('muted')
        elif plot_style in self.matplotx_style_list:
            self.plot_style = getattr(matplotx.styles, plot_style)
        plt.style.use(self.plot_style)

        if self.plot_type == 'ca':
            self.axes_name_dict = {'x': r'Time [h]', 'y': r'current density [$\mathrm{mA/cm^2}$]'}
        if self.plot_type == 'cv':
            self.axes_name_dict = {'x': r'voltage [V .Vs. RHE]', 'y': r'current density [$\mathrm{mA/cm^2}$]'}
        self.half = half
        self.half_check = half_check


    def plt_plot(self, ax, data, half_index=None, label=None):
        if label:
            ax.plot(data[:half_index, 0], data[:half_index, 1], label=label)
            ax.set_xlabel(self.axes_name_dict['x'])
            ax.set_ylabel(self.axes_name_dict['y'])
        else:
            ax.plot(data[:half_index, 0], data[:half_index, 1])
            ax.set_xlabel(self.axes_name_dict['x'])
            ax.set_ylabel(self.axes_name_dict['y'])


    def plot(self):
        separated_fig, separated_ax = plt.subplots()
        all_fig, all_ax = plt.subplots()
        for folder in self.storage_data_dict.keys():
            if os.path.isdir(folder):
                normalized_data_folder = folder + '/' + 'normalized_data'
                pic_folder = folder + '/' + 'pic'
                dir_check(pic_folder, delete=False)
                data_list = []
                filename_list = []
                for filename in os.listdir(normalized_data_folder):
                    data = np.loadtxt(f"{normalized_data_folder}/{filename}")
                    data_list.append(data)
                    filename_list.append(filename)
                if self.plot_type == 'cv':
                    if self.workstation_type == 'kst':
                        if self.half:
                            data_length = data_list[0].shape[0]
                            for data, filename in zip(data_list, filename_list):
                                if data.shape[0] > data_length * self.half_check:
                                    half_index = int(data.shape[0]/2)
                                else:
                                    half_index = int(data.shape[0])
                                self.plt_plot(separated_ax, data, half_index=half_index)
                                self.plt_plot(all_ax, data, half_index=half_index, label=filename[:-4].replace('_', ' '))
                                separated_fig.savefig(f"{pic_folder}/half_{filename[:-4]}.png", bbox_inches="tight")
                                separated_ax.cla()
                                plt.close(separated_fig)
                            all_ax.legend()
                            all_fig.savefig(f"{pic_folder}/half_all.png", bbox_inches="tight")
                            all_ax.cla()
                            plt.close(all_fig)
                        else:
                            for data, filename in zip(data_list, filename_list):
                                self.plt_plot(separated_ax, data)
                                self.plt_plot(all_ax, data, label=filename[:-4].replace('_', ' '))
                                separated_fig.savefig(f"{pic_folder}/half_{filename[:-4]}.png", bbox_inches="tight")
                                separated_ax.cla()
                                plt.close()
                            all_ax.legend()
                            all_fig.savefig(f"{pic_folder}/half_all.png", bbox_inches="tight")
                            all_ax.cla()
                            plt.close(all_fig)

                    if self.workstation_type == 'ch':
                        for data, filename in zip(data_list, filename_list):
                            self.plt_plot(separated_ax, data)
                            self.plt_plot(all_ax, data, label=filename[:-4].replace('_', ' '))
                            separated_fig.savefig(f"{pic_folder}/{filename[:-4]}.png", bbox_inches="tight")
                            separated_ax.cla()
                            plt.close()
                        all_ax.legend()
                        all_fig.savefig(f"{pic_folder}/all.png", bbox_inches="tight")
                        all_ax.cla()
                        plt.close()

                if self.plot_type == 'ca':
                    for data, filename in zip(data_list, filename_list):
                        self.plt_plot(separated_ax, data)
                        separated_fig.savefig(f"{pic_folder}/{filename[:-4]}.png", bbox_inches="tight")
                        separated_ax.cla()
                        plt.close()
                    total_data = np.vstack(data_list)
                    self.plt_plot(separated_ax, data)
                    separated_fig.savefig(f"{pic_folder}/all.png", bbox_inches="tight")
                    separated_ax.cla()
                    plt.close()
            print(f"plot of {folder} is done")

