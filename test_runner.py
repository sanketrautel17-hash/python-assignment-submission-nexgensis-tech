import os
import json
import subprocess
import sys

# folder where the test case files live
TEST_CASES_DIR = os.path.join(os.path.dirname(__file__), "Python Assignment(Delivery System Test Cases)")
BASE_CASE = os.path.join(os.path.dirname(__file__), "base_case.json")
EXCLUDED = {"report.json"}  # output files that should not be treated as inputs
SIMULATOR = os.path.join(os.path.dirname(__file__), "simulator.py")


def run_simulator(input_file):
    result = subprocess.run(
        [sys.executable, SIMULATOR, input_file],
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def get_report_path(input_file):
    return os.path.join(os.path.dirname(os.path.abspath(input_file)), "report.json")


def read_report(report_path):
    # read the report manually to check the raw string format too
    with open(report_path, 'r') as f:
        raw = f.read()
    data = json.loads(raw)
    return data, raw


def check_report(data, raw, input_file):
    errors = []

    # load the original input to know how many packages there were
    with open(input_file, 'r') as f:
        input_data = json.load(f)
    total_packages = len(input_data["packages"])

    # check 1: best_agent key exists
    if "best_agent" not in data:
        errors.append("missing 'best_agent' key")

    # check 2: total packages delivered should equal total packages in input
    delivered_sum = 0
    for key, val in data.items():
        if key == "best_agent":
            continue
        delivered_sum += val.get("packages_delivered", 0)

    if delivered_sum != total_packages:
        errors.append(
            f"packages mismatch: input has {total_packages} packages "
            f"but report shows {delivered_sum} delivered"
        )

    # check 3: efficiency calculation is correct and format is 2 decimal places
    for key, val in data.items():
        if key == "best_agent":
            continue

        pd = val.get("packages_delivered", 0)
        td = val.get("total_distance", 0)
        eff = val.get("efficiency")

        if pd == 0:
            # agent with no packages should have efficiency null
            if eff is not None:
                errors.append(f"{key}: expected efficiency null for 0 packages, got {eff}")
        else:
            # efficiency should be total_distance / packages_delivered
            expected_eff = td / pd
            if eff is None:
                errors.append(f"{key}: efficiency is null but agent has {pd} packages")
            elif abs(eff - expected_eff) > 0.01:
                errors.append(
                    f"{key}: efficiency mismatch — got {eff}, expected ~{expected_eff:.2f}"
                )

    # check 4: 2 decimal places in the raw output string
    # we check by looking for patterns like "50.0" (one decimal) which would be wrong
    import re
    # find all decimal numbers in the output
    numbers = re.findall(r'\d+\.\d+', raw)
    for num in numbers:
        decimal_part = num.split('.')[1]
        if len(decimal_part) != 2:
            errors.append(f"precision error: '{num}' doesn't have exactly 2 decimal places")

    return errors


def run_all_tests():
    all_files = [BASE_CASE]

    test_files = sorted([
        os.path.join(TEST_CASES_DIR, f)
        for f in os.listdir(TEST_CASES_DIR)
        if f.endswith(".json") and f not in EXCLUDED
    ])
    all_files.extend(test_files)

    passed = 0
    failed = 0

    print("=" * 55)
    print("  FastBox Simulator — Test Runner")
    print("=" * 55)

    for input_file in all_files:
        label = os.path.basename(input_file)
        returncode, stdout, stderr = run_simulator(input_file)

        if returncode != 0:
            print(f"  FAIL  {label}")
            print(f"        Simulator crashed: {stderr.strip()}")
            failed += 1
            continue

        report_path = get_report_path(input_file)

        if not os.path.exists(report_path):
            print(f"  FAIL  {label}")
            print(f"        report.json was not created")
            failed += 1
            continue

        try:
            data, raw = read_report(report_path)
        except Exception as e:
            print(f"  FAIL  {label}")
            print(f"        Could not parse report.json: {e}")
            failed += 1
            continue

        errors = check_report(data, raw, input_file)

        if errors:
            print(f"  FAIL  {label}")
            for err in errors:
                print(f"        - {err}")
            failed += 1
        else:
            print(f"  PASS  {label}")
            passed += 1

    print("=" * 55)
    print(f"  Results: {passed} passed, {failed} failed out of {len(all_files)} tests")
    print("=" * 55)


if __name__ == "__main__":
    run_all_tests()
