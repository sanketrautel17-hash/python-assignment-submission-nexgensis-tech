import json
import math
import sys
import os


def load_data(filepath):
    # open and read the json file
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


# warehouses and agents can come in two formats depending on the test case
# format 1: {"W1": [0, 0]}  or  format 2: [{"id": "W1", "location": [0, 0]}]
# this function handles both and returns a normal dict either way
def normalize_locations(items):
    if isinstance(items, dict):
        return items

    result = {}
    for item in items:
        result[item["id"]] = item["location"]
    return result


def euclidean(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def assign_packages(agents, packages, warehouses):
    agent_ids = list(agents.keys())
    assignments = {}
    for a in agent_ids:
        assignments[a] = []

    for package in packages:
        # some files use "warehouse_id", some use "warehouse"
        wid = package.get("warehouse_id") or package.get("warehouse")
        wloc = warehouses[wid]

        nearest = None
        min_dist = 99999

        for a in agent_ids:
            d = euclidean(agents[a], wloc)
            if d < min_dist:
                min_dist = d
                nearest = a

        assignments[nearest].append(package)

    return assignments


def simulate(agents, assignments, warehouses):
    results = {}

    for agent_id in assignments:
        packages = assignments[agent_id]
        pos = list(agents[agent_id])
        total = 0.0
        count = 0

        for p in packages:
            wid = p.get("warehouse_id") or p.get("warehouse")
            wloc = warehouses[wid]
            dest = p["destination"]

            # go from current position to warehouse first
            total += euclidean(pos, wloc)
            # then warehouse to destination
            total += euclidean(wloc, dest)

            # agent is now at the destination, update position
            pos = dest
            count += 1

        if count > 0:
            eff = total / count
        else:
            eff = None

        results[agent_id] = {
            "packages_delivered": count,
            "total_distance": total,
            "efficiency": eff
        }

    return results


def find_best_agent(results):
    best = None
    best_eff = 99999

    for agent_id in results:
        eff = results[agent_id]["efficiency"]
        if eff is None:
            continue
        if eff < best_eff:
            best_eff = eff
            best = agent_id

    return best


def write_report(results, best_agent, output_path):
    # build the json manually so decimal places stay as 2
    # using json.dumps causes 50.0 instead of 50.00
    lines = []

    for agent_id in results:
        d = results[agent_id]
        dist_str = f"{d['total_distance']:.2f}"
        if d["efficiency"] is not None:
            eff_str = f"{d['efficiency']:.2f}"
        else:
            eff_str = "null"

        line = f'  "{agent_id}": {{"packages_delivered": {d["packages_delivered"]}, "total_distance": {dist_str}, "efficiency": {eff_str}}}'
        lines.append(line)

    lines.append(f'  "best_agent": "{best_agent}"')

    final = "{\n" + ",\n".join(lines) + "\n}"

    with open(output_path, 'w') as f:
        f.write(final)

    print(f"report saved to {output_path}")


def run(input_path):
    if not os.path.exists(input_path):
        print("file not found:", input_path)
        quit()

    data = load_data(input_path)

    warehouses = normalize_locations(data["warehouses"])
    agents = normalize_locations(data["agents"])
    packages = data["packages"]

    assignments = assign_packages(agents, packages, warehouses)
    results = simulate(agents, assignments, warehouses)
    best = find_best_agent(results)

    output_path = os.path.join(os.path.dirname(os.path.abspath(input_path)), "report.json")
    write_report(results, best, output_path)

    # print summary
    print("\nDelivery Report:")
    for agent_id in results:
        eff = results[agent_id]["efficiency"]
        eff_str = f"{eff:.2f}" if eff is not None else "null"
        print(f"  {agent_id} -> packages: {results[agent_id]['packages_delivered']}, distance: {results[agent_id]['total_distance']:.2f}, efficiency: {eff_str}")
    print(f"  best agent: {best}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python simulator.py <input.json>")
        quit()

    run(sys.argv[1])
