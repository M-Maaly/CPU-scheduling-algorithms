# CPU Scheduling Algorithms Visualizer

This project is a Python application with a modern GUI to visualize different CPU scheduling algorithms.  
You can add processes, choose a scheduling algorithm, run the simulation, and see the Gantt chart along with waiting and turnaround times.

---

## Features

- FCFS (First Come First Served)
- SJF (Non-Preemptive Shortest Job First)
- SRTF (Preemptive Shortest Remaining Time First)
- Priority Scheduling (Non-Preemptive)
- Round Robin (Time Quantum Scheduling)
- Interactive GUI built with **Tkinter + ttkbootstrap**
- Gantt chart visualization using **Matplotlib**
- Stats table showing Waiting Time & Turnaround Time

---

## Installation

```bash
pip install matplotlib ttkbootstrap
```

## Run the app ForEach(file):
```
python app.py
```
```
python main.py
```

## 1. FCFS (First Come First Served)

### Description:
FCFS executes processes in the order of their arrival. No preemption.

### How it Works:

- Sort processes by arrival time.
- Execute each process fully before moving to the next.
- Waiting time grows when long processes arrive early.
- Time Complexity: O(n log n) (sorting)

### Example:

| Process | Arrival | Burst |
| ------- | ------- | ----- |
| P1      | 0       | 4     |
| P2      | 1       | 3     |
| P3      | 2       | 1     |

### Gantt Chart:
P1 |----4----|
P2      |---3---|
P3           |-1-|

## 2. SJF (Non-Preemptive Shortest Job First)

### Description:
Selects the process with the shortest CPU burst time from the ready queue. Non-preemptive.

### How it Works:

- At each scheduling point, pick the process with the shortest burst time.
- Execute it fully.
- Minimizes average waiting time.
- Time Complexity: O(n²) (due to ready queue sorting each step)

### Example:
| Process | Arrival | Burst |
| ------- | ------- | ----- |
| P1      | 0       | 7     |
| P2      | 2       | 4     |
| P3      | 4       | 1     |

### Gantt Chart:
P1 |---------7---------|
P3                |-1-|
P2                  |----4----|

## 3. SRTF (Shortest Remaining Time First) — Preemptive SJF

### Description:
Preemptive version of SJF. Switches CPU whenever a process with shorter remaining time arrives.

### How it Works:

- Simulate time unit by unit.
- Always pick process with shortest remaining burst.
- Preempt running process if a new shorter process arrives.
- Time Complexity: O(n log n) (using min-heap)

### Example:
| Process | Arrival | Burst |
| ------- | ------- | ----- |
| P1      | 0       | 8     |
| P2      | 1       | 4     |
| P3      | 2       | 2     |

### Gantt Chart:
P1 |--1--|
P3      |--2--|
P2           |----4----|
P1                     |-------7-------|

## 4. Priority Scheduling (Non-Preemptive)

### Description:
Each process has a priority. Lower number = higher priority.
Non-preemptive: once started, process finishes fully.

### How it Works:

- At scheduling point, pick highest priority process.
- If tie → earliest arrival.
- Execute fully.
- Time Complexity: O(n²) (ready queue sorting)

### Example:
| Process | Arrival | Burst | Priority |
| ------- | ------- | ----- | -------- |
| P1      | 0       | 4     | 2        |
| P2      | 1       | 3     | 1        |
| P3      | 2       | 2     | 3        |

### Gantt Chart:
P1 |----4----|
P2      |---3---|
P3           |--2--|

## 5. Round Robin (RR)

### Description:
Time-sharing algorithm. Each process gets a fixed time quantum.

### How it Works:

- Processes wait in a queue.
- Each process runs for min(burst, quantum) time.
- If remaining burst → goes to end of queue.
- Continue until all finish.
- Time Complexity: O(n²) (queue rotations)

### Example (Quantum = 2):
| Process | Arrival | Burst |
| ------- | ------- | ----- |
| P1      | 0       | 5     |
| P2      | 1       | 3     |


## How to Use the GUI
- Add processes with ID, Arrival, Burst, Priority.
- Choose the scheduling algorithm from the dropdown.
- Set Quantum for Round Robin.
- Click Run to see the Gantt chart and stats.
- Load example processes anytime for testing.
