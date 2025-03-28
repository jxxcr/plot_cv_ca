import numpy as np
from .os_operate import dir_check


def file_name_parse(file_name):
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


def split_kst_cv_data(filename, cut=25, dir_name='raw_data'):
    with open(filename, 'r') as f:
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

    dir_check(dir_name, delete=False)

    for i in range(len(data_list_list)):
        with open(f"./{dir_name}/cycle_{i}.dat", 'w') as f:
            f.write(f"#E(V)\ti(A/cm2)\tT(s)\n")
            for j in range(len(data_list_list[i])):
                f.write(f"{data_list_list[i][j][0]}\t{data_list_list[i][j][1]}\t{data_list_list[i][j][2]}\n")


def split_ch_cv_data(filename, separator, cut=13, dir_name='raw_data'):
    with open(filename, 'r') as f:
        data = f.read()

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

    dir_check(dir_name, delete=False)

    for i in range(len(data_list_list)):
        with open(f"./{dir_name}/cycle_{i}.dat", 'w') as f:
            for j in range(len(data_list_list[i])):
                f.write(f"{data_list_list[i][j][0]}\t{data_list_list[i][j][1]}\n")


def cv_correction(data, pH, area, reference, dir_name='normalized_data', file_name='a', half=True):
    if half:
        x = data[:int(data.shape[0]/2), 0] + reference + 0.059*pH
        y = (data[:int(data.shape[0]/2), 1]*1000) / area
    else:
        x = data[:, 0] + 0.197 + 0.059*pH
        y = (data[:, 1]*1000) / area

    dir_check(dir_name, delete=False)

    with open(f"./{dir_name}/{file_name}", 'w') as f:
        f.write(f"#E(V .Vs. RHE)\ti(mA/cm2)\n")
        for i in range(len(x)):
            f.write(f"{x[i]}\t{y[i]}\n")


def ca_correction(data, area, dir_name='normalized_data', file_name='a'):
    x = data[:, 2] / 3600
    y = (data[:, 1]*1000) / area

    dir_check(dir_name, delete=False)

    with open(f"./{dir_name}/{file_name}", 'w') as f:
        f.write(f"#T(h)\ti(mA/cm2)\n")
        for i in range(len(x)):
            f.write(f"{x[i]}\t{y[i]}\n")


def ch_ca_correction(data, area, dir_name='normalized_data', file_name='a'):
    x = data[:, 0] / 3600
    y = (data[:, 1]*1000) / area

    dir_check(dir_name, delete=False)

    with open(f"./{dir_name}/{file_name}", 'w') as f:
        f.write(f"#T(h)\ti(mA/cm2)\n")
        for i in range(len(x)):
            f.write(f"{x[i]}\t{y[i]}\n")


