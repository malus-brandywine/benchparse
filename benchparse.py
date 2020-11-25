import argparse
import json
import os
from pathlib import Path
from matplotlib import pyplot as plt, rcParams

def main():
    args = parse_args()
    benchmarks_requested = load_benchmarks_requested(args.benchmarks)
    benchmarks_json = load_benchmarks_json(args.bench_output)
    outfile = get_filename(args.benchparse_output)
    benchmarks_dict = load_benchmarks_dict(benchmarks_requested, benchmarks_json, outfile)
    generate_and_save_summary_stats(benchmarks_dict, outfile)
    # generate_and_save_plots(benchmarks_dict, args.benchparse_output)

def parse_args():
    parser = argparse.ArgumentParser(description='Parse sel4bench output')
    parser.add_argument('-b', '--bench-output', type=str, metavar='', required=True, help='File containing output of sel4bench')
    parser.add_argument('-i', '--benchmarks', type=str, metavar='', required=True, help='File with a list of line-separated benchmarks')
    parser.add_argument('-o', '--benchparse-output', type=str, metavar='', required=True, help='File to write benchparse output to')
    return parser.parse_args()

def load_benchmarks_requested(benchreqs_infile):
    benchmarks_requested = []
    with open(benchreqs_infile, 'r') as breqs:
        benchmarks_requested = breqs.readlines()
    benchmarks_requested = set([line.strip().lower() for line in benchmarks_requested])
    return benchmarks_requested

def load_benchmarks_json(benchoutput_infile):
    with open(benchoutput_infile, 'r') as bout:
        bench_lines = bout.readlines()
    for line in range(len(bench_lines)):
        if bench_lines[line].strip() == 'JSON OUTPUT':
            bench_results = bench_lines[line + 1].replace('END JSON OUTPUT', '')
            bench_json = json.loads(bench_results)
    return bench_json

def load_benchmarks_dict(benchmarks_requested, benchmarks_json, outfile):
    benchmarks = {}
    with open(outfile + '.json', 'w+') as jout:
        for benchmark in benchmarks_json:
            if benchmark['Benchmark'].lower() in benchmarks_requested:
                benchmarks[benchmark['Benchmark']] = benchmark['Results']
                json.dump(benchmark, jout, indent=4)
    return benchmarks

def generate_and_save_summary_stats(benchmarks_dict, outfile):
    output = ''
    for benchmark in benchmarks_dict:
        min = benchmarks_dict[benchmark][0]['Min']
        max = benchmarks_dict[benchmark][0]['Max']
        mean = benchmarks_dict[benchmark][0]['Mean']
        stddev = benchmarks_dict[benchmark][0]['Stddev']
        nsamples = benchmarks_dict[benchmark][0]['Samples']
        output += f'{benchmark}:\n'
        output += f'Min: {min:.2f}\n'
        output += f'Max: {max:.2f}\n'
        output += f'Mean: {mean:.2f}\n'
        output += f'StdDev: {stddev:.2f}\n'
        output += f'Samples: {nsamples}\n'
        output += '\n'
    print(output)
    with open(outfile + '.txt', 'w+') as tout:
        tout.write(output)

def generate_and_save_plots(benchmarks_dict, outfile):
    rcParams['figure.figsize'] = 10, 6
    f = plt.figure()
    for benchmark in benchmarks_dict:
        plt.plot(benchmarks_dict[benchmark][0]['Raw results'], label=benchmark)
    plt.title('Signalling a Notification')
    plt.ylabel('Clock Cycles')
    plt.xlabel('Iteration')
    plt.ylim(0, 1750)
    plt.legend(loc='upper right')
    plt.grid()
    f.savefig(outfile + '.pdf')

def get_filename(outfile):
    prefix = 1
    while os.path.exists(f'{outfile}/0{prefix}.txt'):
        prefix += 1
    return f'{outfile}/0{prefix}'

if __name__ == '__main__':
    main()