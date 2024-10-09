# This benchmark is to access the performance and scalability of kwant model.
# Key parameters:
# Model_size N: the number of grid units in length direction

'''
run python benchmark.py template_name
'''

import time
import psutil

import os
import numpy as np
import matplotlib.pyplot as plt

from xkwant.batch import *
from xkwant.templates import *
from xkwant.physics import *
from xkwant.utils import *
from xkwant.config import LATTICE_CONST_HGTE
import xkwant.templates as mytemplates


def benchmark_model(template, model_size=10):
    process = psutil.Process(os.getpid())
    start_time = time.time()
    memory_before = process.memory_info().rss

    energy_range = np.arange(0.1, 0.5, 0.01)
    Iin = 10e-9  # A
    N1 = model_size
    L = LATTICE_CONST_HGTE * N1
    geop = dict(
        a=L / N1,
        lx_leg=int(N1),
        ly_leg=int(N1 / 6),
        lx_neck=int(N1 / 6),
        ly_neck=int(N1 / 6),
    )

    hamp_sys = dict(ts=0, ws=0.1, vs=0.3, ms=0.05, Wdis=0, invs=0, hybs=0)
    hamp_lead = dict(tl=0, wl=0.1, vl=0.3, ml=0.05, invl=0, hybl=0)

    syst = template(geop, hamp_sys, hamp_lead)  # This system won't be changed anymore
    get_idos(syst, energy_range)
    # energy = np.mean(energy_range)
    # vvector_4t(syst, energy, [0, 0, Iin, -Iin])
    # rho_j_energy_site(syst, energy)

    end_time = time.time()

    memory_after = process.memory_info().rss

    execution_time = end_time - start_time
    memory_usage = memory_after - memory_before
    num_sites = syst.area / geop["a"] ** 2

    return num_sites, execution_time, memory_usage


def run_benchmark(template,model_sizes):
    results = []
    for model_size in model_sizes:
        print(f"running model_size={model_size}")
        num_sites, execution_time, memory_usage = benchmark_model(template,model_size)
        results.append(
            {
                "model_size": model_size,
                "num_sites": num_sites,
                "execution_time": execution_time,
                "memory_usage": memory_usage,
            }
        )
    return results


if __name__ == "__main__":
    import pandas as pd
    import matplotlib.pyplot as plt
    import sys

    # Modify model_sizes
    model_sizes = [10, 10, 20, 50] # the first run of model_sizes == "10" will includes overhead time for starting the calculation, thus will be removed in statistic data. 


    if len(sys.argv) == 1:
        print("No additional argument is provided. Default model type: mkhbar_4t will be benchmarked!")
        template = mkhbar_4t
    elif len(sys.argv) == 2:
        template_name = sys.argv[1]
        try:
            template = getattr(mytemplates,template_name) # Dynamically get the template from the module using getattr
        except AttributeError:
            print(f"template {template_name} not found in the module xkwant.templates")
            sys.exit(1)
    else:
        raise AttributeError("too many arguments! template as the only argument is allowed")


    results = run_benchmark(template,model_sizes)
    # Convert results to a DataFrame
    df = pd.DataFrame(results)
    # Plot the results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    ax1.scatter(
        df["model_size"].tolist()[1:],
        df["execution_time"].tolist()[1:],
        label=f"Execution Time ",
    )
    ax2.scatter(
        df["num_sites"].tolist()[1:],
        df["execution_time"].tolist()[1:],
        label=f"Memory Usage",
    )
    ax1.set_xlabel("Model Size in 1D")
    ax2.set_xlabel("Number of Sites (2D)")
    ax1.set_ylabel("Execution Time [Second]")
    ax2.set_ylabel("Execution Time [Second]")
    plt.show()
