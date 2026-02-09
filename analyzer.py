import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import csv
import os
import platform

# -----------------------------
# App Setup
# -----------------------------
root = tk.Tk()
root.title("Student Marks Analyzer")
root.geometry("700x750")
root.minsize(600, 650)

# -----------------------------
# Theme Config
# -----------------------------
light_bg = "#f4f6f8"
dark_bg = "#1e1e1e"
light_fg = "#000000"
dark_fg = "#ffffff"

is_dark = False

subjects = []
marks = []

# -----------------------------
# Theme Toggle
# -----------------------------
def toggle_theme():
    global is_dark
    is_dark = not is_dark
    bg = dark_bg if is_dark else light_bg
    fg = dark_fg if is_dark else light_fg

    root.config(bg=bg)
    for widget in root.winfo_children():
        try:
            widget.config(bg=bg, fg=fg)
        except:
            pass

# -----------------------------
# Core Functions
# -----------------------------
def add_subject():
    sub = subject_entry.get().strip()
    mark = marks_entry.get().strip()

    if not sub or not mark:
        messagebox.showwarning("Input Error", "Enter subject and marks")
        return

    try:
        mark = int(mark)
        if not 0 <= mark <= 100:
            raise ValueError
    except:
        messagebox.showerror("Invalid Marks", "Marks must be 0–100")
        return

    subjects.append(sub)
    marks.append(mark)
    listbox.insert(tk.END, f"{sub:<20} : {mark}")
    subject_entry.delete(0, tk.END)
    marks_entry.delete(0, tk.END)

def analyze():
    global report_text_data

    name = name_entry.get().strip()
    roll = roll_entry.get().strip()

    if not name or not roll:
        messagebox.showerror("Missing Info", "Enter Name and Roll No")
        return

    if not marks:
        messagebox.showerror("No Data", "Add at least one subject")
        return

    total = sum(marks)
    avg = total / len(marks)
    percentage = avg

    if percentage >= 90:
        grade, status = "A+", "Excellent"
    elif percentage >= 80:
        grade, status = "A", "Very Good"
    elif percentage >= 70:
        grade, status = "B", "Good"
    elif percentage >= 60:
        grade, status = "C", "Average"
    elif percentage >= 40:
        grade, status = "D", "Pass"
    else:
        grade, status = "F", "Fail"

    report_text_data = (
        f"STUDENT RESULT REPORT\n"
        f"-----------------------------\n"
        f"Name        : {name}\n"
        f"Roll No     : {roll}\n\n"
        f"Total Marks : {total}\n"
        f"Average     : {avg:.2f}\n"
        f"Percentage  : {percentage:.2f}%\n"
        f"Grade       : {grade}\n"
        f"Status      : {status}\n"
    )

    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, report_text_data)
    result_text.config(state="disabled")

    save_to_csv(name, roll, total, percentage, grade, status)

def show_graph():
    if not marks:
        messagebox.showerror("No Data", "No marks to show")
        return

    plt.figure(figsize=(7,4))
    plt.bar(subjects, marks)
    plt.ylim(0,100)
    plt.title("Marks Analysis")
    plt.xlabel("Subjects")
    plt.ylabel("Marks")
    plt.tight_layout()
    plt.show()

# -----------------------------
# Save Multiple Students
# -----------------------------
def save_to_csv(name, roll, total, percentage, grade, status):
    file_exists = os.path.isfile("students_data.csv")

    with open("students_data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Name", "Roll", "Total", "Percentage", "Grade", "Status"])
        writer.writerow([name, roll, total, percentage, grade, status])

# -----------------------------
# Export PDF
# -----------------------------
def export_pdf():
    if not result_text.get("1.0", tk.END).strip():
        messagebox.showerror("No Report", "Analyze result first")
        return

    file = filedialog.asksaveasfilename(defaultextension=".pdf")
    if not file:
        return

    c = canvas.Canvas(file, pagesize=A4)
    text = c.beginText(40, 800)

    for line in report_text_data.split("\n"):
        text.textLine(line)

    c.drawText(text)
    c.save()

    messagebox.showinfo("Success", "PDF Exported Successfully")

# -----------------------------
# Print
# -----------------------------
def print_report():
    if platform.system() == "Windows":
        file = "temp_report.txt"
        with open(file, "w") as f:
            f.write(report_text_data)
        os.startfile(file, "print")
    else:
        messagebox.showinfo("Print", "Print supported on Windows only")

# -----------------------------
# UI Layout
# -----------------------------
root.config(bg=light_bg)

header = tk.Label(root, text="🎓 Student Marks Analyzer", font=("Segoe UI", 20, "bold"))
header.pack(pady=10)

main = tk.Frame(root)
main.pack(fill="both", expand=True, padx=15)

# Student Info
tk.Label(main, text="Student Name").grid(row=0, column=0, sticky="w")
name_entry = tk.Entry(main, width=30)
name_entry.grid(row=1, column=0)

tk.Label(main, text="Roll Number").grid(row=0, column=1, sticky="w")
roll_entry = tk.Entry(main, width=20)
roll_entry.grid(row=1, column=1)

# Subject Entry
tk.Label(main, text="Subject").grid(row=2, column=0, sticky="w")
subject_entry = tk.Entry(main, width=30)
subject_entry.grid(row=3, column=0)

tk.Label(main, text="Marks").grid(row=2, column=1, sticky="w")
marks_entry = tk.Entry(main, width=20)
marks_entry.grid(row=3, column=1)

tk.Button(main, text="Add Subject", command=add_subject).grid(row=3, column=2, padx=10)

listbox = tk.Listbox(main, height=8)
listbox.grid(row=4, column=0, columnspan=3, sticky="we", pady=10)

# Buttons
tk.Button(main, text="Analyze", command=analyze).grid(row=5, column=0)
tk.Button(main, text="Graph", command=show_graph).grid(row=5, column=1)
tk.Button(main, text="Dark Mode", command=toggle_theme).grid(row=5, column=2)

# Result Area
result_text = tk.Text(main, height=10, state="disabled")
result_text.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=10)

# Export / Print
tk.Button(main, text="Export PDF", command=export_pdf).grid(row=7, column=0)
tk.Button(main, text="Print", command=print_report).grid(row=7, column=1)

# Grid weights
for i in range(3):
    main.columnconfigure(i, weight=1)
main.rowconfigure(6, weight=1)

root.mainloop()
