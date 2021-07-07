import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import os
import re
from scipy.stats import gmean

pwd = Path(os.path.dirname(os.path.realpath(__file__)))


def geo_mean(iterable):
    a = np.array(iterable)
    return a.prod()**(1.0 / len(a))


def match_num_thread(line):
    """
    Args:
        line: a line of text.
    Return:
        Returns None if not matched.
        Returns OMP_NUM_THREADS value if matched.
    Ref:
        https://www.tutorialspoint.com/python/python_reg_expressions.htm
    """
    pattern = r"^# OMP_NUM_THREADS: ([0-9]+)$"
    match = re.match(pattern, line)
    if match:
        return int(match.group(1))
    else:
        return None


def match_runtime(line):
    """
    Args:
        line: a line of text.
    Return:
        Returns None if not matched.
        Returns the runtime value (float) if the value is matched.
    Ref:
        https://stackoverflow.com/a/14550569/1255535
    """
    pattern = r"^.* +(\d+(?:\.\d+)?) ms +.*ms +([0-9]+)$"
    match = re.match(pattern, line)
    if match:
        return float(match.group(1)) / float(match.group(2))
    else:
        return None


def extract_cpu_prefix(filename):
    """
    Input:
        benchmark_Intel(R)_Core(TM)_i5-8265U_CPU_with_dummy.log
    Output:
        benchmark_Intel(R)_Core(TM)_i5-8265U_CPU
    """
    pattern = r"^(.*_CPU).*$"
    match = re.match(pattern, filename)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Invalid log file {filename}")


def parse_file(log_file):
    """
    Returns: results, a list of directories, e.g.
        [
            {"num_threads": xxx, "gmean": xxx, "ICP": xxx, "Tensor": xxx},
            {"num_threads": xxx, "gmean": xxx, "ICP": xxx, "Tensor": xxx},
        ]
    """
    results = []
    with open(log_file) as f:
        lines = [line.strip() for line in f.readlines()]

        current_num_thread = None
        current_runtimes = []
        for line in lines:
            # Parse current line
            num_thread = match_num_thread(line)
            runtime = match_runtime(line)

            if num_thread:
                # If we already collected, save
                if current_num_thread:
                    results.append({
                        "num_threads": current_num_thread,
                        "gmean": gmean(current_runtimes)
                    })
                # Reset to fresh
                current_num_thread = num_thread
                current_runtimes = []
            elif runtime:
                current_runtimes.append(runtime)

        # Save the last set of data
        if current_num_thread:
            results.append({
                "num_threads": current_num_thread,
                "gmean": gmean(current_runtimes)
            })
    return results


if __name__ == '__main__':
    log_files = sorted(list(pwd.glob('benchmark_*.log')))
    log_files = [str(log_file) for log_file in log_files]

    cpu_prefixes = set([extract_cpu_prefix(log_file) for log_file in log_files])
    map_cpu_prefix_to_log_files = dict()
    for cpu_prefix in cpu_prefixes:
        map_cpu_prefix_to_log_files[cpu_prefix] = []
        for log_file in log_files:
            if log_file.startswith(cpu_prefix):
                map_cpu_prefix_to_log_files[cpu_prefix].append(log_file)
        map_cpu_prefix_to_log_files[cpu_prefix] = sorted(
            map_cpu_prefix_to_log_files[cpu_prefix])
    print(map_cpu_prefix_to_log_files)

    for cpu_prefix in map_cpu_prefix_to_log_files:
        log_files = map_cpu_prefix_to_log_files[cpu_prefix]
        num_log_files = len(log_files)
        fig = plt.figure()
        for idx, log_file in enumerate(log_files):
            ax = fig.add_subplot(num_log_files, 1, idx + 1)
            results = parse_file(log_file)
            title = Path(log_file).name[len("benchmark_"):-len(".log")]
            title = title.replace("_", " ")
            xs = [result["num_threads"] for result in results]
            ys = [result["gmean"] for result in results]
            ax.plot(xs, ys, 'b-')
            ax.plot(xs, ys, 'b*')
            for x, y in zip(xs, ys):
                ax.annotate(f"{y:.2f}", xy=(x, y))
            ax.set_ylim(ymin=0)
            ax.set_title(title)
            ax.set_xticks(np.arange(min(xs), max(xs) + 1, 1.0))
            ax.set_xlabel("# of threads")
            ax.set_ylabel("Runtime gmean (ms)")
        fig.tight_layout()

    plt.show()
