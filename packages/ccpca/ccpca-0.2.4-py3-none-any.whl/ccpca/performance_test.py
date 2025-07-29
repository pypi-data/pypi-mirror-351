import time
import numpy as np

from cpca import CPCA, CPCA2
from ccpca import CCPCA, CCPCA2
from contrastive import CPCA as OriginalCPCA


class PerfMetrics:
    def __init__(self, name=None):
        self.name = name
        self.wall_seconds = None
        self.cpu_seconds = None
        self.cpu_seconds_begin = time.process_time()
        self.wall_seconds_begin = time.perf_counter()

    def __enter__(self):
        self.reset()
        return self

    def __exit__(self, type, value, traceback):
        self.check()

    def reset(self):
        self.cpu_seconds_begin = time.process_time()
        self.wall_seconds_begin = time.perf_counter()

    def check(self):
        self.wall_seconds = time.perf_counter() - self.wall_seconds_begin
        self.cpu_seconds = time.process_time() - self.cpu_seconds_begin

    def dict(self):
        if self.name:
            return {
                f"{self.name}.wall_seconds": self.wall_seconds,
                f"{self.name}.cpu_seconds": self.cpu_seconds,
            }
        else:
            return {"wall_seconds": self.wall_seconds, "cpu_seconds": self.cpu_seconds}


data_sizes = [100, 1000, 10000, 100000]  # , 1000000
dim_sizes = [10, 100, 1000]
counts = 5
out = open("result.csv", "w")

for n, m in zip(data_sizes, data_sizes):
    for d in dim_sizes:
        if n >= 1000000 and d >= 1000:
            out.write(str(n) + "," + str(d) + ",,,\n")
            continue

        a = np.float32(np.random.rand(n, d))
        b = np.float32(np.random.rand(m, d))
        out.write(str(n) + "," + str(d))
        print("n:", n, ", d:", d)

        original_cpca_times = []
        cpp_cpca_times = []
        py_cpca_times = []
        cpp_times = []
        py_times = []
        for count in range(counts):
            # cPCA
            # original implementation
            with PerfMetrics() as pm:
                cpca = OriginalCPCA()
                projected_data, alphas = cpca.fit_transform(
                    a, b, n_alphas_to_return=1, return_alphas=True
                )
                end = time.time()
            print("cpca (org)", pm.dict())
            original_cpca_times.append(pm.dict()["wall_seconds"])

            # cpp implementation
            with PerfMetrics() as pm:
                cpca = CPCA()
                cpca.fit(a, b, auto_alpha_selection=False, alpha=1.0)
                end = time.time()
            print("cpca (cpp)", pm.dict())
            py_cpca_times.append(pm.dict()["wall_seconds"])

            # python implementation
            with PerfMetrics() as pm:
                cpca = CPCA2()
                cpca.fit(a, b, auto_alpha_selection=False, alpha=1.0)
                end = time.time()
            print("cpp (py )", pm.dict())
            cpp_times.append(pm.dict()["wall_seconds"])

            # ccPCA
            # cpp implementation
            with PerfMetrics() as pm:
                ccpca = CCPCA()
                ccpca.fit(a, b, var_thres_ratio=0.5, max_log_alpha=1.0)
                end = time.time()
            print("cpp", pm.dict())
            cpp_times.append(pm.dict()["wall_seconds"])

            # python implementation
            with PerfMetrics() as pm:
                ccpca = CCPCA2()
                ccpca.fit(a, b, var_thres_ratio=0.5, max_log_alpha=1.0)
                end = time.time()
            print("py", pm.dict())
            py_times.append(pm.dict()["wall_seconds"])

        out.write("," + str(np.mean(np.array(original_cpca_times))))
        out.write("," + str(np.mean(np.array(cpp_cpca_times))))
        out.write("," + str(np.mean(np.array(py_cpca_times))))
        out.write("," + str(np.mean(np.array(cpp_times))))
        out.write("," + str(np.mean(np.array(py_times))))
        out.write("\n")

out.close()
