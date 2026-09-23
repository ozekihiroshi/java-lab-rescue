#!/usr/bin/env python3
"""Read-only Linux host capacity snapshot. Never starts, pulls or stops containers."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

GIB = 1024 ** 3


def assess(memory, learners):
    # Current public configuration: Hub <=1 GiB, each learner <=3 GiB.
    # Keep 0.5 GiB additional available; existing workloads can still grow.
    required = int((1 + 3 * learners + 0.5) * GIB)
    available = memory['MemAvailable']
    return {'learners': learners, 'required_available_gib': required / GIB,
            'available_gib': round(available / GIB, 2),
            'memory_budget_pass': available >= required}


def snapshot(learners):
    memory = {line.split(':')[0]: int(line.split()[1]) * 1024
              for line in Path('/proc/meminfo').read_text().splitlines()}
    result = assess(memory, learners)
    result.update(total_gib=round(memory['MemTotal'] / GIB, 2),
                  swap_used_gib=round((memory['SwapTotal'] - memory['SwapFree']) / GIB, 2),
                  logical_cpus=os.cpu_count(), root_free_gib=round(shutil.disk_usage('/').free / GIB, 2))
    try:
        proc = subprocess.run(['docker', 'stats', '--no-stream', '--format', '{{json .}}'],
                              capture_output=True, text=True, timeout=20)
        result['docker_stats_available'] = proc.returncode == 0
        result['containers'] = [json.loads(line) for line in proc.stdout.splitlines()] if proc.returncode == 0 else []
    except (OSError, subprocess.TimeoutExpired):
        result['docker_stats_available'] = False
        result['containers'] = []
    result['note'] = 'Snapshot only; not an admission guarantee. Account for workload growth, CPU and disk before deployment.'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--learners', type=int, default=1)
    args = parser.parse_args()
    if args.learners < 1:
        parser.error('--learners must be positive')
    try:
        result = snapshot(args.learners)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result['memory_budget_pass'] and result['docker_stats_available'] else 2)
    except (OSError, KeyError, ValueError) as error:
        parser.exit(2, 'Capacity check unavailable: ' + str(error) + '\n')
