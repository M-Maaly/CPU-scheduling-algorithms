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
