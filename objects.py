import tkinter as tk
from tkinter import ttk, messagebox


class Process:
    def __init__(self, name:str, arrival_time:int, burst_time:int, priority:int=3):
        self.name = name
        self.arrival_time = arrival_time
        self.original_burst_time = burst_time
        self.burst_time = burst_time
        self.original_priority = priority
        self.priority = priority
        self.first_response = 0
        self.sub_wait_time = 0
        self.processed_time = 0
        self.processing_time = 0
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0

    def complete(self, time):
        self.completion_time = time
        self.turnaround_time = self.completion_time - self.arrival_time
    
    def is_completed(self):
        return self.burst_time == 0

    def increase_priority(self):
        self.priority -= 1
        self.sub_wait_time = 0
    
    def decrease_priority(self):
        self.priority += 1
        self.processed_time = 0
    
    def wait(self):
        self.sub_wait_time += 1
    
    def process(self):
        self.processed_time += 1
        self.burst_time -= 1
    
    def __str__(self):
        return f"{self.name} (burst_time: {str(self.burst_time)}, processed_time: {str(self.processed_time)}, sub_wait_time: {str(self.sub_wait_time)}, arrival_time: {str(self.arrival_time)})"


class ProcessCard(tk.Frame):
    def __init__(self, parent, process:Process):
        super().__init__(parent, bd=1, relief="solid", padx=5, pady=2)
        self.process = process
        tk.Label(self, text=process.name, font=("Arial", 12, "bold"), width=4, bg="lightblue").pack(side=tk.LEFT, padx=2)
        stats_frame = tk.Frame(self)
        stats_frame.pack(side=tk.LEFT, padx=2)
        self.burst_label = tk.Label(stats_frame, text=f"BT:{process.burst_time}")
        self.burst_label.pack(anchor='w')
        self.processed_label = tk.Label(stats_frame, text=f"PT:{process.processed_time}")
        self.processed_label.pack(anchor='w')
        self.arrival_label = tk.Label(stats_frame, text=f"AT:{process.arrival_time}")
        self.arrival_label.pack(anchor='w')
        self.pack(side=tk.LEFT, padx=5)
    
    def update_values(self):
        self.burst_label.configure(text=f"BT:{self.process.burst_time}")
        self.processed_label.configure(text=f"PT:{self.process.processed_time}")
        self.arrival_label.configure(text=f"AT:{self.process.arrival_time}")


class ModifyWindow(tk.Toplevel):
    def __init__(self, processes:list[Process], process_table):
        super().__init__()
        self.processes = processes
        self.outer_process_table = process_table

        self.title("Modify Processes & Parameters")
        self.geometry("900x500")

        # Process Table
        table_frame = tk.Frame(self)
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        columns = ("Process", "Arrival Time", "Burst Time", "Priority")
        self.process_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.process_table.heading(col, text=col)
            self.process_table.column(col, width=100)

        for p in processes:
            self.process_table.insert("", "end", values=(p.name, p.arrival_time, p.original_burst_time, p.original_priority))

        self.process_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.process_table.yview)
        self.process_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.process_table.bind("<Double-1>", self.on_double_click)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        tk.Button(button_frame, text="Add Process", command=self.add_blank_process).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Process", command=self.delete_selected_process).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Processes", command=self.clear_table).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save", command=self.save_all).pack(side=tk.LEFT, padx=5)
    
    def clear_table(self):
        for child in self.process_table.get_children():
            self.process_table.delete(child)
    
    def on_double_click(self, event):
        item = self.process_table.identify_row(event.y)
        column = self.process_table.identify_column(event.x)
        if not item or column == "#0":
            return
        x, y, width, height = self.process_table.bbox(item, column)
        value = self.process_table.set(item, column)
        entry = tk.Entry(self.process_table)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()
        
        entry.bind("<Return>", lambda event: self.save_edit(item, column, entry))
        entry.bind("<FocusOut>", lambda event: self.save_edit(item, column, entry))
    
    def save_edit(self, item, column, entry, event=None):
        self.process_table.set(item, column, entry.get())
        entry.destroy()
    
    def add_blank_process(self):
        self.process_table.insert("", "end", values=("", "", "", ""))
    
    def delete_selected_process(self):
        selected = self.process_table.selection()
        if not selected:
            messagebox.showwarning("Delete", "No process selected.")
            return
        for item in selected:
            self.process_table.delete(item)
    
    def save_all(self):
        new_processes:list[Process] = []
        for item in self.process_table.get_children():
            pid, arrival, burst, priority = self.process_table.item(item, 'values')
            if pid and arrival and burst and priority:
                try:
                    arrival_val = int(arrival)
                    burst_val = int(burst)
                    priority_val = int(priority)
                    if arrival_val < 0 or burst_val <= 0 or priority_val not in [1, 2, 3, 4]:
                        messagebox.showerror("Error", f"Invalid values for {pid}.")
                        return
                    new_processes.append(Process(pid, arrival_val, burst_val, priority_val))
                except ValueError:
                    messagebox.showerror("Error", f"Invalid input in process {pid}")
                    return
        
        self.processes.clear()
        self.processes.extend(new_processes)

        for row in self.outer_process_table.get_children():
            self.outer_process_table.delete(row)
        for p in self.processes:
            self.outer_process_table.insert("", "end", values=(p.name, p.arrival_time, p.original_burst_time, p.priority))
        messagebox.showinfo("Saved", "Processes and parameters updated successfully!")
        self.destroy()


class GanttCard(tk.Frame):
    color = ["red", "orange", "blue", "green"]

    def __init__(self, gantt_inner, current_process:Process):
        super().__init__(gantt_inner, bd=1, relief='solid', padx=5, pady=2, bg=self.color[current_process.priority-1], width=current_process.burst_time * 20)
        self.current_process = current_process
        color = self.color[current_process.priority-1]
        tk.Label(self, text=current_process.name, font=("Arial", 10, "bold"), bg=color).pack(side=tk.LEFT)
        stats = tk.Frame(self, bg=color)
        stats.pack(side=tk.LEFT, padx=2)
        self.burst_label = tk.Label(stats, text=f"BT:{current_process.burst_time}", bg=color)
        self.burst_label.pack(anchor='w')
        self.processed_label = tk.Label(stats, text=f"PT:{current_process.processed_time}", bg=color)
        self.processed_label.pack(anchor='w')
        self.arrival_label = tk.Label(stats, text=f"AT:{current_process.arrival_time}", bg=color)
        self.arrival_label.pack(anchor='w')
        self.pack(side=tk.LEFT, padx=2, pady=2)
    
    def update_values(self):
        self.burst_label.configure(text=f"BT:{self.current_process.burst_time}")
        self.processed_label.configure(text=f"PT:{self.current_process.processed_time}")
        self.arrival_label.configure(text=f"AT:{self.current_process.arrival_time}")


class GanttChart(tk.Canvas):
    def __init__(self, gantt_frame, scheduling_algo:str):
        super().__init__(gantt_frame, bg='white', height=100)
        self.scroll = tk.Scrollbar(gantt_frame, orient=tk.HORIZONTAL, command=self.xview)
        self.configure(xscrollcommand=self.scroll.set)
        
        self.gantt_inner = tk.Frame(self, bg="white")
        self.create_window((0, 0), window=self.gantt_inner, anchor="nw")
        self.gantt_inner.bind("<Configure>", lambda event: self.configure(scrollregion=self.bbox("all")))
    
    def all_pack(self):
        self.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.scroll.pack(side=tk.TOP, fill=tk.X)