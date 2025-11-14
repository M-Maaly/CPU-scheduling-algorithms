# main.py
import heapq
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ---------------- Scheduling Algorithms ---------------- #
def fcfs(processes):
    procs = sorted(processes, key=lambda p: p["arrival"])
    time = 0
    gantt = []
    stats = {}
    for p in procs:
        start = max(time, p["arrival"])
        finish = start + p["burst"]
        gantt.append((p["id"], start, finish))
        wt = start - p["arrival"]
        tat = finish - p["arrival"]
        stats[p["id"]] = {"waiting": wt, "turnaround": tat}
        time = finish
    return gantt, stats

def sjf_non_preemptive(processes):
    procs = sorted(processes, key=lambda p: p["arrival"])
    time = 0
    i = 0
    ready = []
    gantt = []
    stats = {}
    n = len(procs)
    while i < n or ready:
        while i < n and procs[i]["arrival"] <= time:
            ready.append(procs[i])
            i += 1
        if not ready:
            time = procs[i]["arrival"]
            continue
        ready.sort(key=lambda x: x["burst"])
        p = ready.pop(0)
        start = time
        finish = start + p["burst"]
        gantt.append((p["id"], start, finish))
        stats[p["id"]] = {"waiting": start - p["arrival"], "turnaround": finish - p["arrival"]}
        time = finish
    return gantt, stats

def srtf_preemptive(processes):
    # SRTF: simulate time unit by unit
    procs = sorted(processes, key=lambda p: p["arrival"])
    n = len(procs)
    remaining = {p["id"]: p["burst"] for p in procs}
    arrival_map = {p["id"]: p["arrival"] for p in procs}
    time = 0
    i = 0
    heap = []
    current = None
    gantt = []
    start_time = None
    finished = set()
    while len(finished) < n:
        # push arrivals
        while i < n and procs[i]["arrival"] <= time:
            heapq.heappush(heap, (remaining[procs[i]["id"]], procs[i]["id"]))
            i += 1
        if not heap:
            time += 1
            continue
        # pick shortest remaining
        rem, pid = heapq.heappop(heap)
        if current != pid:
            # switching process
            if current is not None and start_time is not None:
                gantt.append((current, start_time, time))
            current = pid
            start_time = time
        # execute 1 unit
        remaining[pid] -= 1
        time += 1
        if remaining[pid] > 0:
            heapq.heappush(heap, (remaining[pid], pid))
        else:
            # finished
            gantt.append((pid, start_time, time))
            finished.add(pid)
            start_time = None
            current = None
    # compute stats
    stats = {}
    for p in procs:
        pid = p["id"]
        # turnaround = finish_time - arrival
        # find last finish in gantt for pid
        finishes = [seg[2] for seg in gantt if seg[0] == pid]
        finish = max(finishes) if finishes else p["arrival"]
        burst = p["burst"]
        tat = finish - p["arrival"]
        wt = tat - burst
        stats[pid] = {"waiting": wt, "turnaround": tat}
    # merge adjacent segments of same pid (to make chart cleaner)
    merged = []
    for seg in gantt:
        if merged and merged[-1][0] == seg[0] and merged[-1][2] == seg[1]:
            merged[-1] = (merged[-1][0], merged[-1][1], seg[2])
        else:
            merged.append(seg)
    return merged, stats

def priority_non_preemptive(processes):
    procs = sorted(processes, key=lambda p: p["arrival"])
    time = 0
    i = 0
    ready = []
    gantt = []
    stats = {}
    n = len(procs)
    while i < n or ready:
        while i < n and procs[i]["arrival"] <= time:
            ready.append(procs[i])
            i += 1
        if not ready:
            time = procs[i]["arrival"]
            continue
        ready.sort(key=lambda x: (x.get("priority", 0), x["arrival"]))
        p = ready.pop(0)
        start = time
        finish = start + p["burst"]
        gantt.append((p["id"], start, finish))
        stats[p["id"]] = {"waiting": start - p["arrival"], "turnaround": finish - p["arrival"]}
        time = finish
    return gantt, stats

def round_robin(processes, quantum=2):
    procs = sorted(processes, key=lambda p: p["arrival"])
    from collections import deque
    time = 0
    i = 0
    q = deque()
    remaining = {p["id"]: p["burst"] for p in procs}
    arrivals = {p["id"]: p["arrival"] for p in procs}
    gantt = []
    last_exec = {}
    # load initial arrivals
    while i < len(procs) and procs[i]["arrival"] <= time:
        q.append(procs[i])
        i += 1
    if not q and i < len(procs):
        time = procs[i]["arrival"]
        q.append(procs[i]); i+=1
    while q:
        p = q.popleft()
        pid = p["id"]
        start = time
        exec_time = min(quantum, remaining[pid])
        time += exec_time
        remaining[pid] -= exec_time
        gantt.append((pid, start, time))
        # push newly arrived processes while we executed
        while i < len(procs) and procs[i]["arrival"] <= time:
            q.append(procs[i]); i += 1
        if remaining[pid] > 0:
            q.append(p)
    # stats
    stats = {}
    for p in procs:
        pid = p["id"]
        finishes = [seg[2] for seg in gantt if seg[0] == pid]
        finish = max(finishes) if finishes else p["arrival"]
        tat = finish - p["arrival"]
        wt = tat - p["burst"]
        stats[pid] = {"waiting": wt, "turnaround": tat}
    # merge contiguous
    merged = []
    for seg in gantt:
        if merged and merged[-1][0] == seg[0] and merged[-1][2] == seg[1]:
            merged[-1] = (merged[-1][0], merged[-1][1], seg[2])
        else:
            merged.append(seg)
    return merged, stats

# ---------------- GUI App ---------------- #
class SchedulerApp:
    def __init__(self, root):
        self.root = root
        root.title("CPU Scheduling Visualizer — Modern GUI")
        root.geometry("1000x650")
        self.style = tb.Style("cosmo")  # modern theme

        # Left frame: controls + process table
        left = ttk.Frame(root)
        left.pack(side=LEFT, fill=BOTH, padx=10, pady=10, expand=False)

        controls = ttk.LabelFrame(left, text="Processes")
        controls.pack(fill=X, pady=6)

        frm = ttk.Frame(controls)
        frm.pack(fill=X, padx=6, pady=6)

        ttk.Label(frm, text="ID").grid(row=0, column=0, sticky=W, padx=2)
        ttk.Label(frm, text="Arrival").grid(row=0, column=1, sticky=W, padx=2)
        ttk.Label(frm, text="Burst").grid(row=0, column=2, sticky=W, padx=2)
        ttk.Label(frm, text="Priority").grid(row=0, column=3, sticky=W, padx=2)

        self.ent_id = ttk.Entry(frm, width=6)
        self.ent_id.grid(row=1, column=0, padx=2)
        self.ent_arr = ttk.Entry(frm, width=8)
        self.ent_arr.grid(row=1, column=1, padx=2)
        self.ent_burst = ttk.Entry(frm, width=8)
        self.ent_burst.grid(row=1, column=2, padx=2)
        self.ent_pr = ttk.Entry(frm, width=8)
        self.ent_pr.grid(row=1, column=3, padx=2)

        btn_add = ttk.Button(frm, text="Add", bootstyle="success", command=self.add_process)
        btn_add.grid(row=1, column=4, padx=6)

        btn_del = ttk.Button(frm, text="Delete Selected", bootstyle="danger", command=self.delete_selected)
        btn_del.grid(row=2, column=4, padx=6, pady=4)

        btn_load = ttk.Button(frm, text="Load Example", bootstyle="info", command=self.load_example)
        btn_load.grid(row=3, column=4, padx=6, pady=4)

        # process tree
        self.tree = ttk.Treeview(controls, columns=("arrival", "burst", "priority"), show="headings", height=8)
        self.tree.pack(fill=X, padx=6, pady=6)
        for c, w in [("arrival", 80), ("burst", 80), ("priority", 80)]:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=w, anchor=CENTER)
        self.tree["displaycolumns"] = ("arrival", "burst", "priority")
        self.tree["columns"] = ("arrival", "burst", "priority")
        # we'll put id as iid

        # algorithm selection
        algo_frame = ttk.LabelFrame(left, text="Algorithm")
        algo_frame.pack(fill=X, pady=6, padx=0)
        self.algo_var = tk.StringVar(value="FCFS")
        algos = ["FCFS", "SJF (Non-Preemptive)", "SRTF (Preemptive SJF)", "Priority (Non-Preemptive)", "Round Robin"]
        ttk.Label(algo_frame, text="Choose:").grid(row=0, column=0, padx=6, pady=6, sticky=W)
        self.combo = ttk.Combobox(algo_frame, values=algos, textvariable=self.algo_var, state="readonly")
        self.combo.grid(row=0, column=1, padx=6, pady=6)
        self.combo.current(0)

        ttk.Label(algo_frame, text="Quantum (RR):").grid(row=1, column=0, padx=6, sticky=W)
        self.quantum_ent = ttk.Entry(algo_frame, width=8)
        self.quantum_ent.grid(row=1, column=1, padx=6, sticky=W)
        self.quantum_ent.insert(0, "2")

        btn_run = ttk.Button(algo_frame, text="Run", bootstyle="primary", command=self.run)
        btn_run.grid(row=2, column=0, columnspan=2, pady=8)

        # right frame: chart + stats
        right = ttk.Frame(root)
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

        self.fig = Figure(figsize=(7, 3.5))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_yticks([])

        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        stats_frame = ttk.LabelFrame(right, text="Stats (Waiting / Turnaround)")
        stats_frame.pack(fill=BOTH, expand=False, pady=6)

        self.stats_tree = ttk.Treeview(stats_frame, columns=("waiting", "turnaround"), show="headings", height=6)
        self.stats_tree.pack(fill=X, padx=6, pady=6)
        self.stats_tree.heading("waiting", text="Waiting")
        self.stats_tree.heading("turnaround", text="Turnaround")

        # status
        self.status = ttk.Label(root, text="Ready", anchor=W)
        self.status.pack(side=BOTTOM, fill=X)

        self.load_example()

    def add_process(self):
        pid = self.ent_id.get().strip()
        try:
            arr = float(self.ent_arr.get().strip())
            burst = float(self.ent_burst.get().strip())
        except ValueError:
            messagebox.showerror("Input error", "Arrival and Burst must be numbers.")
            return
        pr = self.ent_pr.get().strip()
        pr_val = int(pr) if pr.isdigit() else 0
        if not pid:
            messagebox.showerror("Input error", "Process ID required.")
            return
        # disallow duplicate id
        if pid in self.tree.get_children():
            messagebox.showerror("Input error", "Process ID already exists.")
            return
        self.tree.insert("", "end", iid=pid, values=(arr, burst, pr_val))
        self.ent_id.delete(0, tk.END)
        self.ent_arr.delete(0, tk.END)
        self.ent_burst.delete(0, tk.END)
        self.ent_pr.delete(0, tk.END)

    def delete_selected(self):
        sel = self.tree.selection()
        for s in sel:
            self.tree.delete(s)

    def load_example(self):
        # clear
        for x in self.tree.get_children():
            self.tree.delete(x)
        example = [
            ("P1", 0, 7, 2),
            ("P2", 2, 4, 1),
            ("P3", 4, 1, 3),
            ("P4", 5, 4, 2),
        ]
        for pid, a, b, p in example:
            self.tree.insert("", "end", iid=pid, values=(a, b, p))
        self.status.config(text="Loaded example processes")

    def read_processes(self):
        procs = []
        for iid in self.tree.get_children():
            arr, burst, pr = self.tree.item(iid, "values")
            procs.append({"id": iid, "arrival": float(arr), "burst": float(burst), "priority": int(pr)})
        return procs

    def run(self):
        procs = self.read_processes()
        if not procs:
            messagebox.showwarning("No processes", "Add processes first.")
            return
        algo = self.algo_var.get()
        try:
            if algo == "FCFS":
                gantt, stats = fcfs(procs)
            elif algo == "SJF (Non-Preemptive)":
                gantt, stats = sjf_non_preemptive(procs)
            elif algo == "SRTF (Preemptive SJF)":
                gantt, stats = srtf_preemptive(procs)
            elif algo == "Priority (Non-Preemptive)":
                gantt, stats = priority_non_preemptive(procs)
            elif algo == "Round Robin":
                q = float(self.quantum_ent.get())
                if q <= 0:
                    messagebox.showerror("Quantum error", "Quantum must be > 0")
                    return
                gantt, stats = round_robin(procs, quantum=q)
            else:
                messagebox.showerror("Unknown", "Unknown algorithm selected.")
                return
        except Exception as e:
            messagebox.showerror("Runtime error", str(e))
            return

        # draw gantt
        self.draw_gantt(gantt, title=algo)
        # show stats
        self.show_stats(stats)
        self.status.config(text=f"Ran {algo}")

    def draw_gantt(self, gantt, title="Gantt Chart"):
        self.ax.clear()
        colors = {}
        cmap = self.fig.canvas.get_supported_filetypes()  # dummy to avoid lint; we won't use this
        y = 0.5
        for seg in gantt:
            pid, start, finish = seg
            width = finish - start
            if pid not in colors:
                # generate simple color from hash
                import random
                random.seed(hash(pid) & 0xFFFFFFFF)
                colors[pid] = (random.random()*0.6+0.2, random.random()*0.6+0.2, random.random()*0.6+0.2)
            self.ax.barh(y, width, left=start, height=0.6, align='center', edgecolor='k', color=colors[pid])
            self.ax.text(start + width/2, y, pid, va='center', ha='center', color='white', fontsize=9, fontweight='bold')
            y += 1
        self.ax.set_yticks([])
        self.ax.set_xlabel("Time")
        self.ax.set_title(title)
        # adjust x limits
        starts = [s for (_, s, _) in gantt] if gantt else [0]
        ends = [e for (_, _, e) in gantt] if gantt else [0]
        self.ax.set_xlim(min(starts) - 1 if starts else 0, max(ends) + 1 if ends else 1)
        self.ax.invert_yaxis()
        self.fig.tight_layout()
        self.canvas.draw()

    def show_stats(self, stats):
        for r in self.stats_tree.get_children():
            self.stats_tree.delete(r)
        # sort by process id
        for pid in sorted(stats.keys()):
            self.stats_tree.insert("", "end", iid=pid, values=(stats[pid]["waiting"], stats[pid]["turnaround"]))

def main():
    root = tb.Window()
    app = SchedulerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
