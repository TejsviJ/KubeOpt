from kubernetes import client, config
from datetime import datetime, timezone
import csv
import os
import time


OUTPUT_FILE = "optimizer/data/metrics.csv"
INTERVAL_SECONDS = 15


def cpu_to_millicores(cpu):
    if cpu.endswith("n"):
        return int(cpu[:-1]) / 1_000_000
    elif cpu.endswith("u"):
        return int(cpu[:-1]) / 1_000
    elif cpu.endswith("m"):
        return float(cpu[:-1])
    else:
        return float(cpu) * 1000


def memory_to_mib(memory):
    if memory.endswith("Ki"):
        return int(memory[:-2]) / 1024
    elif memory.endswith("Mi"):
        return float(memory[:-2])
    elif memory.endswith("Gi"):
        return float(memory[:-2]) * 1024
    else:
        return float(memory) / (1024 * 1024)


def collect_metrics(api):
    metrics = api.list_namespaced_custom_object(
        group="metrics.k8s.io",
        version="v1beta1",
        namespace="default",
        plural="pods",
    )

    timestamp = datetime.now(timezone.utc).isoformat()

    rows = []

    for pod in metrics["items"]:
        pod_name = pod["metadata"]["name"]

        labels = pod["metadata"].get("labels", {})

        if labels.get("app") != "api":
            continue

        for container in pod["containers"]:
            usage = container["usage"]

            rows.append({
                "timestamp": timestamp,
                "pod": pod_name,
                "container": container["name"],
                "cpu_millicores": round(cpu_to_millicores(usage["cpu"]), 2),
                "memory_mib": round(memory_to_mib(usage["memory"]), 2),
            })

    return rows


def write_metrics(rows):
    file_exists = os.path.exists(OUTPUT_FILE)

    with open(OUTPUT_FILE, "a", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "pod",
                "container",
                "cpu_millicores",
                "memory_mib",
            ],
        )

        if not file_exists:
            writer.writeheader()

        writer.writerows(rows)


def main():
    try:
        config.load_incluster_config()
        print("Using in-cluster Kubernetes configuration.")
    except config.ConfigException:
        config.load_kube_config()
        print("Using local kubeconfig.")

    api = client.CustomObjectsApi()

    print("KubeOpt metrics collector started.")
    print(f"Collecting every {INTERVAL_SECONDS} seconds...")
    print(f"Writing to {OUTPUT_FILE}")

    while True:
        try:
            rows = collect_metrics(api)
            write_metrics(rows)

            for row in rows:
                print(
                    f"{row['timestamp']} "
                    f"pod={row['pod']} "
                    f"cpu={row['cpu_millicores']}m "
                    f"memory={row['memory_mib']}Mi"
                )

        except Exception as error:
            print(f"Collection error: {error}")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()