import csv
import json
from collections import defaultdict
from pathlib import Path


DATA_FILE = Path("optimizer/data/metrics.csv")
OUTPUT_FILE = Path("optimizer/data/analysis.json")

CPU_REQUEST = 1000
MEMORY_REQUEST = 1024
SAFETY_MARGIN = 1.25


def percentile(values, percentile):
    values = sorted(values)

    if not values:
        return 0

    index = (len(values) - 1) * percentile / 100
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    weight = index - lower

    return values[lower] + (values[upper] - values[lower]) * weight


def load_data():
    pod_data = defaultdict(lambda: {"cpu": [], "memory": []})

    with open(DATA_FILE) as file:
        reader = csv.DictReader(file)

        for row in reader:
            pod = row["pod"]

            pod_data[pod]["cpu"].append(
                float(row["cpu_millicores"])
            )

            pod_data[pod]["memory"].append(
                float(row["memory_mib"])
            )

    return pod_data


def main():
    pod_data = load_data()

    pod_results = []

    for pod, data in pod_data.items():

        cpu_p95 = percentile(data["cpu"], 95)
        memory_p95 = percentile(data["memory"], 95)

        pod_results.append({
            "pod": pod,
            "samples": len(data["cpu"]),
            "cpu_p95": round(cpu_p95, 2),
            "memory_p95": round(memory_p95, 2),
            "recommended_cpu": round(cpu_p95 * SAFETY_MARGIN, 2),
            "recommended_memory": round(
                memory_p95 * SAFETY_MARGIN, 2
            ),
        })

        cpu_p95_values = [
            pod["cpu_p95"]
            for pod in pod_results
        ]

        cpu_min = min(cpu_p95_values)
        cpu_max = max(cpu_p95_values)

        cpu_variation = (cpu_max - cpu_min) / cpu_max

    deployment_cpu = max(
        pod["recommended_cpu"]
        for pod in pod_results
    )

    deployment_memory = max(
        pod["recommended_memory"]
        for pod in pod_results
    )

    if cpu_variation < 0.20:
        variance_status = "consistent"
    else:
        variance_status = "heterogeneous"

    result = {
        "workload": "api",
        "current_request": {
            "cpu_millicores": CPU_REQUEST,
            "memory_mib": MEMORY_REQUEST,
        },

        "workload_behavior": {
            "cpu_variation": round(cpu_variation, 3),
            "status": variance_status,
        },
        "recommended_request": {
            "cpu_millicores": deployment_cpu,
            "memory_mib": deployment_memory,
        },
        "safety_margin": SAFETY_MARGIN,
        "pods": pod_results,
    }

    with open(OUTPUT_FILE, "w") as file:
        json.dump(result, file, indent=2)

    print(f"Analysis written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()