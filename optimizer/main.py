import time

from collector.metrics_collector import collect_metrics, write_metrics
from analyzer.analyze import main as analyze
from recommender import main as recommend

from kubernetes import client, config


INTERVAL_SECONDS = 60


def load_kubernetes_config():
    try:
        config.load_incluster_config()
        print("Using in-cluster Kubernetes configuration.")
    except config.ConfigException:
        config.load_kube_config()
        print("Using local kubeconfig.")


def main():
    load_kubernetes_config()

    api = client.CustomObjectsApi()

    print("KubeOpt optimizer started.")

    while True:
        try:
            # 1. Collect current workload metrics
            rows = collect_metrics(api)
            write_metrics(rows)

            print(f"Collected {len(rows)} metric samples.")

            # 2. Analyze historical data
            analyze()

            # 3. Generate recommendation
            recommend()

        except Exception as error:
            print(f"Optimizer error: {error}")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
