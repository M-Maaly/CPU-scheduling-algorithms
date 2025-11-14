"""
CPU Scheduler - Modern GUI
Tkinter + ttkbootstrap + matplotlib

Features:
- FCFS
- SJF (non-preemptive)
- SRTF (preemptive SJF)
- Priority (non-preemptive)
- Round Robin
- Gantt chart embedded
- Waiting time & Turnaround time calculation
- Simple process table + Add / Remove rows

How to run:
1. Install dependencies:
   pip install matplotlib ttkbootstrap
2. Run:
   python app.py

"""

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq

# ---------------- Scheduling Algorithms ---------------- #

def fcfs(processes):
    procs = sorted(processes, key=lambda x: x['arrival'])
    time = 0
    gantt = []
    results = {}

    for p in procs:
        start = max(time, p['arrival'])
        finish = start + p['burst']
        gantt.append((p['id'], start, finish))
        results[p['id']] = {'start': start, 'finish': finish}
        time = finish

    return gantt, results


def sjf_non_preemptive(processes):
    procs = sorted(processes, key=lambda x: x['arrival'])
    time = 0
    i = 0
    ready = []
    gantt = []
    results = {}
    n = len(procs)

    while i < n or ready:
        while i < n and procs[i]['arrival'] <= time:
            ready.append(procs[i])
            i += 1
        if not ready:
            time = procs[i]['arrival']
            continue
        ready.sort(key=lambda x: x['burst'])
        p = ready.pop(0)
        start = time
        finish = time + p['burst']
        gantt.append((p['id'], start, finish))
        results[p['id']] = {'start': start, 'finish': finish}
        time = finish

    return gantt, results


def sjf_preemptive(processes):
    # SRTF
    procs = sorted(processes, key=lambda x: x['arrival'])
    n = len(procs)
    time = 0
    i = 0
    heap = []  # (remaining, idx, proc)
    remaining = {p['id']: p['burst'] for p in procs}
    gantt = []
    current = None
    start_time = None

    while i < n or heap or current:
        while i < n and procs[i]['arrival'] <= time:
            p = procs[i]
            heapq.heappush(heap, (remaining[p['id']], i, p))
            i += 1

        if current and remaining[current] == 0:
            gantt.append((current, start_time, time))
            current = None

        if heap and (current is None or heap[0][0] < remaining[current]):
            if current:
                gantt.append((current, start_time, time))
            rem, idx, p = heapq.heappop(heap)
            current = p['id']
            start_time = time

        if current:
            remaining[current] -= 1
            time += 1
        else:
            # idle
            if i < n:
                time = procs[i]['arrival']
            else:
                break

    # If last running still has remaining zero at time end, it was added
    # Build results: merge segments
    results = {}
    merged = []
    for seg in gantt:
        pid, s, f = seg
        if merged and merged[-1][0] == pid and merged[-1][2] == s:
            merged[-1] = (pid, merged[-1][1], f)
        else:
            merged.append(seg)
    gantt = merged
    for pid, s, f in gantt:
        if pid not in results:
            results[pid] = {'start': s, 'finish': f}
        else:
            results[pid]['finish'] = f

    return gantt, results


def priority_non_preemptive(processes):
    procs = sorted(processes, key=lambda x: x['arrival'])
    time = 0
    i = 0
    ready = []
    gantt = []
    results = {}
    n = len(procs)

    while i < n or ready:
        while i < n and procs[i]['arrival'] <= time:
            ready.append(procs[i])
            i += 1
        if not ready:
            time = procs[i]['arrival']
            continue
        ready.sort(key=lambda x: (x.get('priority', 0), x['arrival']))
        p = ready.pop(0)
        start = time
        finish = time + p['burst']
        gantt.append((p['id'], start, finish))
        results[p['id']] = {'start': start, 'finish': finish}
        time = finish

    return gantt, results


def round_robin(processes, quantum=2):
    procs = sorted(processes, key=lambda x: x['arrival'])
    time = 0
    q = []
    i = 0
    remaining = {p['id']: p['burst'] for p in procs}
    last_enqueue = {}
    gantt = []

    while i < len(procs) or q:
        while i < len(procs) and procs[i]['arrival'] <= time:
            q.append(procs[i])
            last_enqueue[procs[i]['id']] = procs[i]['arrival']
            i += 1

        if not q:
            if i < len(procs):
                time = procs[i]['arrival']
                continue
            else:
                break

        p = q.pop(0)
        pid = p['id']
        start = time
        run = min(quantum, remaining[pid])
        remaining[pid] -= run
        time += run
        finish = time
        gantt.append((pid, start, finish))

        # enqueue arrivals that came during this quantum
        while i < len(procs) and procs[i]['arrival'] <= time:
            q.append(procs[i])
            last_enqueue[procs[i]['id']] = procs[i]['arrival']
            i += 1

        if remaining[pid] > 0:
            q.append({'id': pid, 'arrival': time, 'burst': 0})  # placeholder with same id

    # merge adjacent segments for same pid
    merged = []
    for seg in gantt:
        if merged and merged[-1][0] == seg[0] and merged[-1][2] == seg[1]:
            merged[-1] = (merged[-1][0], merged[-1][1], seg[2])
        else:
            merged.append(seg)
    gantt = merged

    results = {}
    for pid, s, f in gantt:
        if pid not in results:
            results[pid] = {'start': s, 'finish': f}
        else:
            results[pid]['finish'] = f

    return gantt, results

# ---------------- Utility: compute waiting & turnaround ---------------- #

def compute_metrics(processes, results):
    metrics = {}
    for p in processes:
        pid = p['id']
        if pid in results:
            start = results[pid]['start']
            finish = results[pid]['finish']
            turnaround = finish - p['arrival']
            waiting = turnaround - p['burst']
            metrics[pid] = {'waiting': waiting, 'turnaround': turnaround, 'start': start, 'finish': finish}
        else:
            metrics[pid] = {'waiting': None, 'turnaround': None}
    return metrics

# ---------------- GUI ---------------- #

class App:
    def __init__(self, root):
        self.root = root
        root.title('CPU Scheduler - Modern GUI')
        root.geometry('1000x650')
        style = tb.Style('cyborg')

        # Left frame: process table + controls
        left = ttk.Frame(root, padding=12)
        left.pack(side=LEFT, fill=BOTH, expand=False)

        # Controls
        controls = ttk.LabelFrame(left, text='Controls', padding=8)
        controls.pack(fill=X, pady=6)

        ttk.Label(controls, text='Algorithm:').grid(row=0, column=0, sticky=W)
        self.algo_var = tk.StringVar(value='FCFS')
        algo_menu = ttk.Combobox(controls, textvariable=self.algo_var, state='readonly', width=22)
        algo_menu['values'] = ('FCFS', 'SJF (Non-Preemptive)', 'SRTF (Preemptive SJF)', 'Priority (Non-Preemptive)', 'Round Robin')
        algo_menu.grid(row=0, column=1, padx=6, pady=4)

        ttk.Label(controls, text='Quantum (RR):').grid(row=1, column=0, sticky=W)
        self.quantum_var = tk.IntVar(value=2)
        ttk.Entry(controls, textvariable=self.quantum_var, width=8).grid(row=1, column=1, sticky=W)

        run_btn = ttk.Button(controls, text='Run', bootstyle='success-outline', command=self.run)
        run_btn.grid(row=2, column=0, columnspan=2, pady=8, sticky=EW)

        # Process table
        table_frame = ttk.LabelFrame(left, text='Processes (id, arrival, burst, priority)', padding=8)
        table_frame.pack(fill=BOTH, pady=6)

        self.tree = ttk.Treeview(table_frame, columns=('arrival', 'burst', 'priority'), show='headings', height=8)
        self.tree.heading('arrival', text='Arrival')
        self.tree.heading('burst', text='Burst')
        self.tree.heading('priority', text='Priority')
        self.tree.column('arrival', width=80)
        self.tree.column('burst', width=80)
        self.tree.column('priority', width=80)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        btns = ttk.Frame(left)
        btns.pack(fill=X, pady=6)
        ttk.Button(btns, text='Add Row', command=self.add_row).pack(side=LEFT, padx=4)
        ttk.Button(btns, text='Remove Selected', command=self.remove_selected).pack(side=LEFT, padx=4)
        ttk.Button(btns, text='Load Sample', command=self.load_sample).pack(side=LEFT, padx=4)

        # Right frame: canvas + results
        right = ttk.Frame(root, padding=12)
        right.pack(side=LEFT, fill=BOTH, expand=True)

        self.fig = Figure(figsize=(7,3))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        self.results_box = tk.Text(right, height=8, wrap='none')
        self.results_box.pack(fill=X, pady=6)

        # seed with sample
        self.load_sample()

    def add_row(self):
        # default last id
        idx = len(self.tree.get_children()) + 1
        self.tree.insert('', 'end', values=(0, 1, 0), text=f'P{idx}')
        # set iid as Pid for easier mapping
        iid = f'P{idx}'
        self.tree.item(self.tree.get_children()[-1], text=iid)

    def remove_selected(self):
        sel = self.tree.selection()
        for s in sel:
            self.tree.delete(s)

    def load_sample(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        sample = [
            ('P1', 0, 7, 0),
            ('P2', 2, 4, 0),
            ('P3', 4, 1, 0),
            ('P4', 5, 4, 0),
        ]
        for pid, a, b, pr in sample:
            self.tree.insert('', 'end', iid=pid, values=(a, b, pr))

    def get_processes(self):
        procs = []
        for iid in self.tree.get_children():
            vals = self.tree.item(iid)['values']
            try:
                arrival = int(vals[0])
                burst = int(vals[1])
                priority = int(vals[2]) if len(vals) > 2 else 0
            except Exception:
                raise ValueError('Arrival, Burst and Priority must be integers')
            procs.append({'id': iid, 'arrival': arrival, 'burst': burst, 'priority': priority})
        return procs

    def run(self):
        try:
            procs = self.get_processes()
        except ValueError as e:
            messagebox.showerror('Input error', str(e))
            return

        algo = self.algo_var.get()
        quantum = max(1, self.quantum_var.get())

        if algo == 'FCFS':
            gantt, results = fcfs(procs)
        elif algo == 'SJF (Non-Preemptive)':
            gantt, results = sjf_non_preemptive(procs)
        elif algo == 'SRTF (Preemptive SJF)':
            gantt, results = sjf_preemptive(procs)
        elif algo == 'Priority (Non-Preemptive)':
            gantt, results = priority_non_preemptive(procs)
        elif algo == 'Round Robin':
            gantt, results = round_robin(procs, quantum=quantum)
        else:
            messagebox.showerror('Algorithm error', 'Unknown algorithm')
            return

        metrics = compute_metrics(procs, results)
        self.show_metrics(metrics)
        self.draw_gantt(gantt, title=algo)

    def show_metrics(self, metrics):
        self.results_box.delete('1.0', tk.END)
        lines = []
        total_w = 0
        total_t = 0
        count = 0
        for pid, m in metrics.items():
            if m['waiting'] is None:
                lines.append(f"{pid}: no schedule")
                continue
            lines.append(f"{pid}: Waiting = {m['waiting']}, Turnaround = {m['turnaround']}")
            total_w += m['waiting']
            total_t += m['turnaround']
            count += 1
        if count:
            lines.append(f"Average Waiting = {total_w / count:.2f}")
            lines.append(f"Average Turnaround = {total_t / count:.2f}")
        self.results_box.insert(tk.END, "\n".join(lines))

    def draw_gantt(self, gantt, title='Gantt'):
        self.ax.clear()
        y = 0
        height = 0.6
        colors = {}
        cmap = self.fig.canvas.get_renderer()  # not used for color but placeholder

        # assign a color for each pid
        pids = list({seg[0] for seg in gantt})
        for i, pid in enumerate(pids):
            colors[pid] = f'C{i % 10}'

        for pid, start, finish in gantt:
            self.ax.barh(0, finish - start, left=start, height=height, align='center', color=colors.get(pid))
            self.ax.text((start + finish) / 2, 0, pid, va='center', ha='center', color='white', fontsize=9)

        self.ax.set_ylim(-1, 1)
        self.ax.set_yticks([])
        self.ax.set_xlabel('Time')
        self.ax.set_title(title)
        self.ax.grid(True, axis='x', linestyle='--', alpha=0.4)
        self.canvas.draw()


if __name__ == '__main__':
    root = tb.Window(themename='cosmo')
    app = App(root)
    root.mainloop()
