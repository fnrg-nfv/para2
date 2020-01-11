import collections
import os
import glob
import pickle
from itertools import cycle
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline, BSpline

from para_placement.helper import *


def main_time():
    result = load_and_print(glob.glob("./results/time/total*")[-1])

    x, data = transfer_result(result)

    data['RORP'] = data['RORP time']
    data['heuristic'] = data['greedy time']
    del data['greedy time']
    del data['optimal']
    del data['greedy']
    del data['RORP time']

    print(x, data)
    plt.yscale('log')
    draw_plot(x, data, xlabel='Topology Size', ylabel='Running Time (s)',
              save_file_name='time', colors='rg', linestyles=['--', ':'], markers='^o')


def main_compare():
    filenames = glob.glob("./results/compare/total*")
    filenames.sort()
    result = load_and_print(filenames[-1])

    x, data = transfer_result(result, 0)
    data['NFP-naive'] = data['OM']
    data['Chain w/o parallelism'] = data['NP']
    del data['optimal']
    del data['OM']
    del data['NP']

    print(data)

    draw_plot(x, data, save_file_name='compare_sfc', legends=[
              'Chain w/o parallelism', 'NFP-naive', 'RORP'], colors='mcr', linestyles=['-.', ':', '--'], markers=' x^')


def main_compare_latency():
    filenames = glob.glob("./results/compare/total*")
    filenames.sort()
    result = load_and_print(filenames[-1])

    x, data = transfer_result(result, 2)
    data['NFP-naive'] = data['OM']
    data['Chain w/o parallelism'] = data['NP']
    del data['optimal']
    del data['OM']
    del data['NP']

    draw_plot(x, data, ylabel='Latency (ms)', save_file_name='compare_latency', legends=[
              'Chain w/o parallelism', 'NFP-naive', 'RORP'], colors='mcr', linestyles=['-.', ':', '--'], markers=' x^')


def main_vl2():
    filenames = glob.glob("./results/VL2/01*")
    filenames.sort()
    result = load_and_print(filenames[-1])
    x, data = transfer_result(result, index=0)
    add_zero(x, data)
    print(x, data)
    draw_plot(x, data, legends=['optimal', 'RORP',
                                'heuristic'], save_file_name='vl2')


def main_fattree():
    filenames = glob.glob("./results/fattree/01*")
    filenames.sort()
    result = load_and_print(filenames[-1])
    x, data = transfer_result(result, index=0)
    add_zero(x, data)
    print(x, data)
    draw_plot(x, data, legends=['optimal', 'RORP',
                                'heuristic'], save_file_name='fattree')


def main_bcube():
    filenames = glob.glob("./results/Bcube/01*")
    filenames.sort()
    result = load_and_print(filenames[-2])
    x, data = transfer_result(result, index=0)
    add_zero(x, data)
    print(x, data)
    draw_plot(x, data, legends=['optimal', 'RORP',
                                'heuristic'], save_file_name='bcube')


def load_and_print(filename):
    print(filename)
    d = load_file(filename)
    print_dict(d)
    return d


def print_dict(d):
    for k in d:
        print(k, d[k])
    print()


def main_k():
    filenames = glob.glob("./results/k/total_*")
    filenames.sort()
    result = load_and_print(filenames[-3])
    result.update(load_and_print(filenames[-2]))
    result.update(load_and_print(filenames[-1]))

    del result[4096]
    del result[1536]
    x = np.array([k for k in result])
    x.sort()

    rorp_y = np.array([result[i]['RORP'][0] for i in x])
    rorp_time_y = np.array([result[i]['RORP time'] for i in x])
    print(x, rorp_y,  rorp_time_y)

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel("k")
    ax1.set_ylabel("Number of Accepted Requests", color=color)
    ax1.set_ylim(60, 100)
    ax1.plot(x, rorp_y, color=color, linestyle='--', marker='^', linewidth=2)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.set_ylabel("Time (s)", color=color)
    ax2.plot(x, rorp_time_y, color=color,
             linestyle=':', marker='x', linewidth=1.5)
    ax2.set_ylim(200, 1800)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.grid(linestyle='--')

    if input("Save this eps?(y/N)") == 'y':
        plt.savefig('eps/k.eps', format='eps')
    # Note: plt.savefig() must before plt.show()
    plt.show()


def transfer_result(result, index=-1):
    x = [key for key in result]  # number of sfc requests
    x.sort()
    legends = [l for l in result[x[0]]]

    data = {}
    if index >= 0:
        data = {legend: [result[size][legend][index]
                         for size in x] for legend in legends}
    else:
        data = {legend: [result[size][legend]
                         for size in x] for legend in legends}

    return x, data


def add_zero(x, data):
    x.insert(0, 0)
    for legend in data:
        data[legend].insert(0, 0)


def draw_plot(x, data,
              legends=[],
              save_file_name='',
              xlabel='Number of SFC Requests',
              ylabel="Accepted Requests",
              title='',
              colors='brgcmk',
              markers='s^ox',
              linestyles=['-', '--', ':']):

    color_cy = cycle(colors)
    marker_cy = cycle(markers)
    linestyle_cy = cycle(linestyles)
    if not legends:
        legends = [k for k in data]
    for legend in legends:
        plt.plot(x, data[legend], marker=next(marker_cy), label=legend, color=next(color_cy), linewidth=2,
                 linestyle=next(linestyle_cy))

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(linestyle='--')
    plt.legend()

    if save_file_name:
        write = True
        save_file_name = './eps/{}.eps'.format(save_file_name)
        if os.path.exists(save_file_name):
            if input("Overwrite File?(y/N)") != "y":
                write = False
        if write:
            plt.savefig(save_file_name, format='eps')

    plt.show()


if __name__ == '__main__':
    main_time()
