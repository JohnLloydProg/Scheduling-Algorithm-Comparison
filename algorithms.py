from objects import Process, ProcessCard, GanttCard, GanttChart
import tkinter as tk

class ScedulingAlgorithm:
    chart:GanttChart = None
    queue_frame:tk.Frame = None
    current_process:Process = None
    current_card:GanttCard = None
    processes:list[Process] = []
    queue:list

    def __init__(self, name):
        self.queue = []
        self.name = name
        self.stats = tk.StringVar()

    def finished(self):
        return all(process.is_completed() for process in self.processes)

    def process(self, sim_time):
        pass

    def select(self) -> Process:
        pass


class FirstComeFirstServe(ScedulingAlgorithm):
    def __init__(self):
        super().__init__("First Come First Serve")
    
    def process(self, sim_time):
        if (self.current_process):
            self.current_process.process()
            if (self.current_card):
                self.current_card.update_values()
            if (self.current_process.is_completed()):
                self.current_process.complete(sim_time)
                self.current_process = self.select()
                if (self.current_process):
                    if (not self.current_process.first_response):
                        self.current_process.first_response = sim_time
        else:
            self.current_process = self.select()
            if (self.current_process):
                if (not self.current_process.first_response):
                    self.current_process.first_response = sim_time

    def select(self):
        assert self.chart != None
        try:
            current_process = self.queue.pop(0)
            self.current_card = GanttCard(self.chart.gantt_inner, current_process)
            return current_process
        except:
            return None

class ShortestJobFirst(ScedulingAlgorithm):
    def __init__(self):
        super().__init__("Shortest Job First (Non-preemptive)")

    def process(self, sim_time):
        if (self.current_process):
            self.current_process.process()
            if (self.current_card):
                self.current_card.update_values()
            if (self.current_process.is_completed()):
                self.current_process.complete(sim_time)
                self.current_process = self.select()
                if (self.current_process):
                    if (not self.current_process.first_response):
                        self.current_process.first_response = sim_time
        else:
            self.current_process = self.select()
            if (self.current_process):
                if (not self.current_process.first_response):
                    self.current_process.first_response = sim_time

    def select(self):
        assert self.chart != None
        try:
            # choose shortest remaining burst; tie-break by arrival, then numeric PID
            idx = None
            best_key = None
            for i, p in enumerate(self.queue):
                pid_num = int(p.name[1:]) if p.name[1:].isdigit() else 10**9
                key = (p.burst_time, p.arrival_time, pid_num)
                if (best_key is None) or (key < best_key):
                    best_key = key
                    idx = i

            current_process = self.queue.pop(idx) if (idx is not None) else None
            if (current_process):
                self.current_card = GanttCard(self.chart.gantt_inner, current_process)
            return current_process
        except:
            return None

# Round Robin Algorithmm

class RoundRobin(ScedulingAlgorithm):
    def __init__(self, quantum_time:int=3):
        super().__init__(f"Round Robin (q={quantum_time})")
        self.quantum_time = quantum_time
        self.time_in_quantum = 0
    
    def process(self, sim_time):
        # If we have a running process, run it for one tick
        if self.current_process:
            self.current_process.process()
            self.time_in_quantum += 1
            if self.current_card:
                self.current_card.update_values()
            # On completion, finalize and pick next
            if self.current_process.is_completed():
                self.current_process.complete(sim_time)
                self.current_process = self.select()
                self.time_in_quantum = 0
                if self.current_process and not self.current_process.first_response:
                    self.current_process.first_response = sim_time
            # Quantum expired: preempt and requeue
            elif self.time_in_quantum >= self.quantum_time:
                self.queue.append(self.current_process)
                self.current_process = self.select()
                self.time_in_quantum = 0
                if self.current_process and not self.current_process.first_response:
                    self.current_process.first_response = sim_time
        else:
            # No running process: try to select one
            self.current_process = self.select()
            self.time_in_quantum = 0
            if self.current_process and not self.current_process.first_response:
                self.current_process.first_response = sim_time

    def select(self):
        assert self.chart != None
        try:
            current_process = self.queue.pop(0)
            self.current_card = GanttCard(self.chart.gantt_inner, current_process)
            return current_process
        except:
            return None


# SRTF (Preemptive Shortest Remaining Time First)
class ShortestRemainingTimeFirst(ScedulingAlgorithm):
    def __init__(self):
        super().__init__("Shortest Remaining Time First (Preemptive)")

    def process(self, sim_time:int):
        # Preemption check: if a process in the queue has shorter remaining time than current, preempt
        if self.current_process:
            candidate_idx = self._best_queue_idx()
            if candidate_idx is not None and self.queue[candidate_idx].burst_time < self.current_process.burst_time:
                # preempt current
                self.queue.append(self.current_process)
                self.current_process = self.queue.pop(candidate_idx)
                self.current_card = GanttCard(self.chart.gantt_inner, self.current_process)
                if not self.current_process.first_response:
                    self.current_process.first_response = sim_time

        else:
            # no current, pick best
            self.current_process = self._pop_best_from_queue()
            if self.current_process and not self.current_process.first_response:
                self.current_process.first_response = sim_time

        # Run one tick if we have a process
        if self.current_process:
            self.current_process.process()
            if self.current_card:
                self.current_card.update_values()
            if self.current_process.is_completed():
                self.current_process.complete(sim_time)
                self.current_process = self._pop_best_from_queue()
                if self.current_process and not self.current_process.first_response:
                    self.current_process.first_response = sim_time

    def _best_queue_idx(self):
        if not self.queue:
            return None
        return min(
            range(len(self.queue)),
            key=lambda i: (
                self.queue[i].burst_time,
                self.queue[i].arrival_time,
                int(self.queue[i].name[1:]) if self.queue[i].name[1:].isdigit() else 10**9
            )
        )

    def _pop_best_from_queue(self) -> Process | None:
        idx = self._best_queue_idx()
        if idx is None:
            return None
        current_process = self.queue.pop(idx)
        self.current_card = GanttCard(self.chart.gantt_inner, current_process)
        return current_process


# Priority (Non-preemptive)
class PriorityScheduling(ScedulingAlgorithm):
    def __init__(self):
        super().__init__("Priority (Non-preemptive)")

    def process(self, sim_time:int):
        if self.current_process:
            self.current_process.process()
            if self.current_card:
                self.current_card.update_values()
            if self.current_process.is_completed():
                self.current_process.complete(sim_time)
                self.current_process = self.select()
                if self.current_process and not self.current_process.first_response:
                    self.current_process.first_response = sim_time
        else:
            self.current_process = self.select()
            if self.current_process and not self.current_process.first_response:
                self.current_process.first_response = sim_time

    def select(self) -> Process | None:
        assert self.chart is not None
        if not self.queue:
            return None
        # lower priority value means higher priority (1 is highest)
        idx = min(
            range(len(self.queue)),
            key=lambda i: (
                self.queue[i].priority,
                self.queue[i].arrival_time,
                int(self.queue[i].name[1:]) if self.queue[i].name[1:].isdigit() else 10**9
            )
        )
        current_process = self.queue.pop(idx)
        self.current_card = GanttCard(self.chart.gantt_inner, current_process)
        return current_process
