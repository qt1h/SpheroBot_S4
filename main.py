import time
from spherov2 import scanner
from spherov2.sphero_edu import SpheroEduAPI
from spherov2.types import Color
import tkinter as tk
from random import randint
from threading import Thread
import matplotlib.pyplot as plt
import cv2
import numpy as np

# Create the main window
root = tk.Tk()
root.title("Robot Trajectory")

# Create a canvas to draw the trajectory on
canvas = tk.Canvas(root, width=700, height=700)
canvas.pack()

# Initialize variables
toy_name='SB-9A4B'
data = []
colors = ["red", "blue", "green", "orange", "purple"]
update_id = None
robot_position = None
robot_radius = 15

# Dictionary that maps direction values to a restricted range
direction_mapping = {i: i if i % 10 == 0 else (i // 10) * 10 for i in range(361)}

def draw_trajectory(data):
    canvas.delete("all")

    if not data:
        return

    # Find max and min x and y values
    x_values = [x for x, y in data]
    y_values = [y for x, y in data]

    if not x_values or not y_values:
        return

    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)

    # Add some padding
    padding = 10
    x_min -= padding
    y_min -= padding
    x_max += padding
    y_max += padding

    # Resize and update the canvas
    canvas.config(width=x_max - x_min, height=y_max - y_min)
    canvas.config(scrollregion=(x_min, y_min, x_max, y_max))

    # Draw the trajectory
    for i in range(len(data) - 1):
        x1, y1 = data[i]
        x2, y2 = data[i + 1]
        canvas.create_line(x1, y1, x2, y2, fill="black")

    # Draw the robot as a red dot
    if robot_position:
        x, y = robot_position
        canvas.create_oval(scale_factor * (x - x_min) - robot_radius + x_offset,
                           scale_factor * (y - y_min) - robot_radius + y_offset,
                           scale_factor * (x - x_min) + robot_radius + x_offset,
                           scale_factor * (y - y_min) + robot_radius + y_offset, fill="red")

def update():
    draw_trajectory(data)

# stop updating
def stop():
    global update_id
    root.after_cancel(update_id)
    
# start updating 
def start():
    global update_id, rep, duration, data
    data.clear()
    rep = int(rep_entry.get())
    duration = int(duration_entry.get())
    update_id = root.after(0, update)
    thread = Thread(target=execute_trajectory)
    thread.start()

def execute_trajectory():
    toy = scanner.find_toy(toy_name)
    with SpheroEduAPI(toy) as droid:
        droid.set_stabilization(False)
        droid.set_main_led(Color(r=0, g=0, b=255))
        for _ in range(rep):
            start_time = time.time()
            while time.time() - start_time < duration:
                droid.set_speed(60)
                direction = randint(0, 360)
                restricted_direction = direction_mapping[direction]
                droid.set_heading(restricted_direction)
                
                location = droid.get_location()
                x = location['x']
                y = location['y']
                robot_position = (x, y)
                data.append(robot_position)
                time.sleep(0.3)  # delay between coordinate updates
                droid.set_speed(0)
                root.update()  # update the UI
            draw_trajectory(data)
        root.update()


def save_graph():
    # Trajectory data
    x_data = [point[0] for point in data]
    y_data = [point[1] for point in data]

    # Create the graph
    plt.plot(x_data, y_data, color='black')
    plt.scatter(x_data[-1], y_data[-1], color='red')

    # Defines its limits
    padding = 10
    x_min, x_max = min(x_data) - padding, max(x_data) + padding
    y_min, y_max = min(y_data) - padding, max(y_data) + padding
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    plt.savefig('graph.png')
    
    # TODO: TRANSFORMER LE GRAPH VIA CONVOLUTIONS
    
    plt.show()


# Create labels and entry fields for repetition and duration
rep_label = tk.Label(root, text="Nombre de répétitions:")
rep_label.pack()
rep_entry = tk.Entry(root)
rep_entry.pack()

duration_label = tk.Label(root, text="Durée de chaque répétition (en secondes):")
duration_label.pack()
duration_entry = tk.Entry(root)
duration_entry.pack()

# Create buttons
start_button = tk.Button(root, text="Start", command=start)
start_button.pack()

save_button = tk.Button(root, text="Enregistrer", command=save_graph)
save_button.pack()

# Run the main loop
root.mainloop()
