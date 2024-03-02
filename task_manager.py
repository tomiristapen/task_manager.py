import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import threading
import pygame
import sys
from pygame.locals import *

pygame.init()

# Pomodoro Timer settings
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 360
BG_COLOR = (25, 20, 20)
FONT_COLOR = (255, 255, 255)
TIMER_FONT_SIZE = 64
BUTTON_FONT_SIZE = 28
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pomodoro Timer')
clock = pygame.time.Clock()
timer_font = pygame.font.Font(None, TIMER_FONT_SIZE)
button_font = pygame.font.Font(None, BUTTON_FONT_SIZE)

pygame.mixer.init()
alarm_sound = pygame.mixer.Sound('audio/audio_clock-alarm.mp3')

pomodoro_time = 25 * 60
short_break_time = 5 * 60
long_break_time = 10 * 60
current_time = pomodoro_time
timer_active = False
start_time = 0
mode = "pomodoro"

buttons = {
    "pomodoro": pygame.Rect(100, 20, 140, 40),
    "short_break": pygame.Rect(250, 20, 140, 40),
    "long_break": pygame.Rect(400, 20, 140, 40),
    "start": pygame.Rect(270, 300, 100, 40)
}

def draw_button(button, text):
    pygame.draw.rect(screen, (0, 128, 128), button)
    text_surf = button_font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=button.center)
    screen.blit(text_surf, text_rect)

def check_button_click(pos):
    global current_time, timer_active, start_time, mode
    for key, button in buttons.items():
        if button.collidepoint(pos):
            if key in ["pomodoro", "short_break", "long_break"]:
                mode = key
                if mode == "pomodoro":
                    current_time = pomodoro_time
                elif mode == "short_break":
                    current_time = short_break_time
                elif mode == "long_break":
                    current_time = long_break_time
                timer_active = False
            elif key == "start":
                if not timer_active:
                    timer_active = True
                    start_time = pygame.time.get_ticks()

def pomodoro_main():
    global current_time, timer_active, mode

    while True:
        screen.fill(BG_COLOR)

        draw_button(buttons["pomodoro"], "Pomodoro")
        draw_button(buttons["short_break"], "Short Break")
        draw_button(buttons["long_break"], "Long Break")
        draw_button(buttons["start"], "Start/Stop")

        mins, secs = divmod(current_time, 60)
        timer_surf = timer_font.render(f"{mins:02d}:{secs:02d}", True, FONT_COLOR)
        screen.blit(timer_surf, (SCREEN_WIDTH // 2 - timer_surf.get_width() // 2, SCREEN_HEIGHT // 2))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    check_button_click(event.pos)

        if timer_active:
            elapsed = (pygame.time.get_ticks() - start_time) // 1000
            if mode == "pomodoro":
                current_time = pomodoro_time - elapsed
            elif mode == "short_break":
                current_time = short_break_time - elapsed
            elif mode == "long_break":
                current_time = long_break_time - elapsed

            if current_time <= 0:
                timer_active = False
                alarm_sound.play()
                if mode == "pomodoro":
                    current_time = pomodoro_time
                elif mode == "short_break":
                    current_time = short_break_time
                elif mode == "long_break":
                    current_time = long_break_time

        pygame.display.update()
        clock.tick(30)

root = tk.Tk()
root.title("Task Manager and Pomodoro Timer")

unique_subjects = []

style = ttk.Style(root)
style.theme_use("default")

columns = ('subject', 'assignment', 'status', 'due_on', 'days_left')
tree = ttk.Treeview(root, columns=columns, show='headings', height=5)

tree.heading('subject', text='Subject')
tree.heading('assignment', text='Assignment')
tree.heading('status', text='Status')
tree.heading('due_on', text='Due on')
tree.heading('days_left', text='Days Left')

tree.tag_configure('not_started', background='#f0f0f0')
tree.tag_configure('in_progress', background='#fff2cc')
tree.tag_configure('done', background='#c6efce')
tree.tag_configure('quiz_exam', background='#ffc7ce')

tasks = []

def refresh_table():
    for item in tree.get_children():
        tree.delete(item)
    for task in tasks:
        status_tag = task[2].replace(" ", "_").lower()
        tree.insert('', tk.END, values=task, tags=(status_tag,))
    update_subjects()

def update_subjects():
    global unique_subjects
    unique_subjects = sorted(list(set(task[0] for task in tasks)))

def add_or_edit_task(subject, assignment, status, due_on, window, edit=False, item=None):
    due_date = datetime.strptime(due_on, "%Y-%m-%d")
    days_left = (due_date - datetime.now()).days + 1
    if days_left < 0:
        days_left_str = f"overdue by {abs(days_left)} days"
    else:
        days_left_str = f"{days_left} days"
    new_task = (subject, assignment, status, due_on, days_left_str)
    if edit:
        tasks[item] = new_task
    else:
        tasks.append(new_task)
        if subject not in unique_subjects:
            unique_subjects.append(subject)
            unique_subjects.sort()
    window.destroy()
    refresh_table()

def open_task_dialog(edit=False, item=None):
    window = tk.Toplevel(root)
    window.title("Edit Task" if edit else "Add Task")

    tk.Label(window, text="Subject:").grid(row=0, column=0)
    subject_entry = ttk.Combobox(window, values=unique_subjects)
    subject_entry.grid(row=0, column=1)
    tk.Label(window, text="Assignment:").grid(row=1, column=0)
    assignment_entry = tk.Entry(window)
    assignment_entry.grid(row=1, column=1)
    tk.Label(window, text="Status:").grid(row=2, column=0)
    status_entry = ttk.Combobox(window, values=["Not Started", "In Progress", "Done", "Quiz/Exam"])
    status_entry.grid(row=2, column=1)
    tk.Label(window, text="Due Date (YYYY-MM-DD):").grid(row=3, column=0)
    due_on_entry = tk.Entry(window)
    due_on_entry.grid(row=3, column=1)

    if edit:
        task = tasks[item]
        subject_entry.set(task[0])
        assignment_entry.insert(0, task[1])
        status_entry.set(task[2])
        due_on_entry.insert(0, task[3])

    tk.Button(window, text="Save", command=lambda: add_or_edit_task(subject_entry.get(), assignment_entry.get(), status_entry.get(), due_on_entry.get(), window, edit, item)).grid(row=4, column=0, columnspan=2)

def open_add_task_dialog():
    open_task_dialog()

def open_edit_task_dialog():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a task to edit.")
        return
    selected_index = list(tree.get_children()).index(selected_item[0])
    open_task_dialog(edit=True, item=selected_index)

def delete_task():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a task to delete.")
        return
    selected_index = list(tree.get_children()).index(selected_item[0])
    tasks.pop(selected_index)
    refresh_table()

def start_pomodoro_thread():
    thread = threading.Thread(target=pomodoro_main)
    thread.start()

tree.pack(side=tk.LEFT, expand=True, fill='both', padx=10, pady=5)
buttons_frame = ttk.Frame(root)
buttons_frame.pack(side=tk.RIGHT, fill='y', padx=10, pady=5)
ttk.Button(buttons_frame, text="Add Task", command=open_add_task_dialog).pack(pady=5)
ttk.Button(buttons_frame, text="Edit Task", command=open_edit_task_dialog).pack(pady=5)
ttk.Button(buttons_frame, text="Delete Task", command=delete_task).pack(pady=5)
ttk.Button(buttons_frame, text="Open Pomodoro Timer", command=start_pomodoro_thread).pack(pady=5)

refresh_table()

root.mainloop()
