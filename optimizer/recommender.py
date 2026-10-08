import json
from pathlib import Path


ANALYSIS_FILE = Path("optimizer/data/analysis.json")


def main():

    with open(ANALYSIS_FILE) as file:
        analysis = json.load(file)

    current = analysis["current_request"]
    recommended = analysis["recommended_request"]
    behavior = analysis["workload_behavior"]

    cpu_change = (
        recommended["cpu_millicores"]
        / current["cpu_millicores"]
        - 1
    ) * 100

    memory_change = (
        recommended["memory_mib"]
        / current["memory_mib"]
        - 1
    ) * 100

    print("\n=== KubeOpt Recommendation ===\n")

    print(f"Workload: {analysis['workload']}")

    print("\nWorkload Behavior")
    print(f"  CPU variation: {behavior['cpu_variation'] * 100:.1f}%")
    print(f"  Status: {behavior['status']}")

    print("\nCPU")
    print(f"  Current request:     {current['cpu_millicores']}m")
    print(f"  Recommended request: {recommended['cpu_millicores']:.0f}m")
    print(f"  Change:              {cpu_change:+.1f}%")

    print("\nMemory")
    print(f"  Current request:     {current['memory_mib']}Mi")
    print(f"  Recommended request: {recommended['memory_mib']:.0f}Mi")
    print(f"  Change:              {memory_change:+.1f}%")

    print("\nDecision")

    if behavior["status"] == "consistent":
        print("  ✓ Replica resource usage is consistent.")

    if cpu_change < 0:
        print("  ✓ CPU request can be reduced.")
    else:
        print("  ! CPU request should not be reduced.")

    if memory_change < 0:
        print("  ✓ Memory request can be reduced.")
    else:
        print("  ! Memory request should not be reduced.")

    print("\nReasoning")

    if memory_change < 0:
        print(
            f"  Memory is significantly over-provisioned. "
            f"Observed P95 usage supports approximately "
            f"{recommended['memory_mib']:.0f}Mi."
        )

    if cpu_change > 0:
        print(
            "  CPU usage is close to the current request, "
            "so reducing CPU would risk throttling."
        )

    print("\nNo Kubernetes resources were modified.")


if __name__ == "__main__":
    main()