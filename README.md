# FastBox Mystery Delivery System

Python assignment that simulates one day of delivery operations for a fictional company called FastBox.

---

## What is the Assignment

There are multiple warehouses, delivery agents, and packages. The goal is to:

1. Read the input data from a JSON file
2. Assign each package to the nearest available agent (based on Euclidean distance from the agent to the package's warehouse)
3. Simulate the delivery — agent picks up the package from the warehouse and delivers it to the destination
4. Calculate total distance traveled and efficiency for each agent
5. Generate a `report.json` file showing the results and the best performing agent

---

## How We Solved It

### 1. Reading the JSON file
We open the file manually using Python's built-in `open()` and parse it with `json.load()`. No third-party libraries used.

### 2. Handling different input formats
The input JSON can have warehouses and agents in two different formats — either a plain dictionary or a list of objects. We normalize both into the same format before doing anything else.

### 3. Assigning packages to agents
For each package, we calculate the Euclidean distance from every agent's starting location to the package's warehouse. The package gets assigned to the closest agent. If two agents are equally close, the one that appears first in the input file is chosen.

The formula used:
```
distance = sqrt((x2 - x1)^2 + (y2 - y1)^2)
```

### 4. Simulating deliveries
Each agent delivers their assigned packages one by one in the order they appear in the input file.

For every package:
- Agent travels from current position → warehouse
- Then from warehouse → destination
- Agent's position updates to the destination after each delivery

This is called sequential simulation — the agent doesn't reset to their starting point after each delivery.

### 5. Efficiency
```
efficiency = total_distance / packages_delivered
```
The agent with the lowest efficiency value is the best agent (they covered less distance per package).

### 6. Generating the report
The report is written to `report.json`. Numbers are formatted to exactly 2 decimal places. If an agent received no packages, their efficiency is shown as `null`.

Example output:
```json
{
  "A1": {"packages_delivered": 2, "total_distance": 121.21, "efficiency": 60.61},
  "A2": {"packages_delivered": 2, "total_distance": 79.21, "efficiency": 39.60},
  "A3": {"packages_delivered": 1, "total_distance": 14.14, "efficiency": 14.14},
  "best_agent": "A3"
}
```

---

## Project Structure

```
assignment/
├── simulator.py        <- main script, run this
├── test_runner.py      <- tests all input files automatically
├── base_case.json      <- sample input provided with the assignment
├── report.json         <- output file (generated when you run the simulator)
└── Python Assignment(Delivery System Test Cases)/
    ├── test_case_1.json
    ├── test_case_2.json
    └── ... (up to test_case_10.json)
```

---

## How to Run

### Step 1 — Open terminal in the project folder

```bash
cd C:\Users\munna\my_projects\assissgnment
```

### Step 2 — Run on a single file

```bash
python simulator.py base_case.json
```

This will print a summary in the terminal and save the output to `report.json`.

To run on a specific test case:
```bash
python simulator.py "Python Assignment(Delivery System Test Cases)/test_case_1.json"
```

### Step 3 — Run all test cases at once

```bash
python test_runner.py
```

This runs the simulator on the base case and all 10 test cases and prints PASS or FAIL for each one.

Expected output:
```
=======================================================
  FastBox Simulator - Test Runner
=======================================================
  PASS  base_case.json
  PASS  test_case_1.json
  PASS  test_case_2.json
  ...
  PASS  test_case_10.json
=======================================================
  Results: 11 passed, 0 failed out of 11 tests
=======================================================
```

---

## Requirements

No external libraries needed. Only Python standard library is used:
- `json` — for reading the input file
- `math` — for Euclidean distance calculation
- `os`, `sys` — for file paths and command line arguments
