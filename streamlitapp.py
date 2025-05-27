import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from io import BytesIO
from PIL import Image
import os

# --- Disk Scheduling Algorithms ---
def fcfs(requests, head):
    seek_sequence = [head] + requests
    total_seek = sum(abs(seek_sequence[i] - seek_sequence[i + 1]) for i in range(len(seek_sequence) - 1))
    return seek_sequence, total_seek

def sstf(requests, head):
    requests = requests[:]
    seek_sequence = [head]
    total_seek = 0
    while requests:
        closest = min(requests, key=lambda x: abs(x - head))
        total_seek += abs(head - closest)
        seek_sequence.append(closest)
        head = closest
        requests.remove(closest)
    return seek_sequence, total_seek

def scan(requests, head, max_cylinder=200):
    left = sorted([r for r in requests if r < head], reverse=True)
    right = sorted([r for r in requests if r >= head])
    seek_sequence = [head] + right + [max_cylinder - 1] + left
    total_seek = sum(abs(seek_sequence[i] - seek_sequence[i + 1]) for i in range(len(seek_sequence) - 1))
    return seek_sequence, total_seek

def cscan(requests, head, max_cylinder=200):
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])
    seek_sequence = [head] + right + [max_cylinder - 1, 0] + left
    total_seek = sum(abs(seek_sequence[i] - seek_sequence[i + 1]) for i in range(len(seek_sequence) - 1))
    return seek_sequence, total_seek

def look(requests, head):
    left = sorted([r for r in requests if r < head], reverse=True)
    right = sorted([r for r in requests if r >= head])
    seek_sequence = [head] + right + left
    total_seek = sum(abs(seek_sequence[i] - seek_sequence[i + 1]) for i in range(len(seek_sequence) - 1))
    return seek_sequence, total_seek

def clook(requests, head):
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])
    seek_sequence = [head] + right + left
    total_seek = sum(abs(seek_sequence[i] - seek_sequence[i + 1]) for i in range(len(seek_sequence) - 1))
    return seek_sequence, total_seek

# --- Explanation Generator ---
def get_seek_explanation(path):
    explanation = []
    total = 0
    for i in range(len(path) - 1):
        diff = abs(path[i + 1] - path[i])
        total += diff
        explanation.append(f"|{path[i+1]} - {path[i]}| = {diff}")
    explanation_text = "\n".join(explanation)
    return f"Steps:\n{explanation_text}\n\nTotal Seek Time = {total}"

# --- Streamlit UI ---
st.set_page_config(page_title="Disk Visualizer", layout="wide")
st.title("🧠 Disk Scheduling Visualizer")

with st.sidebar:
    st.header("⚙️ Configuration")
    algo = st.selectbox("Select Algorithm (Simulate Single)", ["FCFS", "SSTF", "SCAN", "CSCAN", "LOOK", "CLOOK"])
    algo1 = st.selectbox("Compare: First Algorithm", ["FCFS", "SSTF", "SCAN", "CSCAN", "LOOK", "CLOOK"])
    algo2 = st.selectbox("Compare: Second Algorithm", ["FCFS", "SSTF", "SCAN", "CSCAN", "LOOK", "CLOOK"])
    queue_input = st.text_input("Enter request queue (comma separated)", "98,183,37,122,14,124,65,67")
    head = st.number_input("Initial Head Position", value=53)
    simulate = st.button("🚀 Simulate")
    compare = st.button("🆚 Compare")

def get_result(algo, queue, head):
    if algo == "FCFS":
        return fcfs(queue, head)
    elif algo == "SSTF":
        return sstf(queue, head)
    elif algo == "SCAN":
        return scan(queue, head)
    elif algo == "CSCAN":
        return cscan(queue, head)
    elif algo == "LOOK":
        return look(queue, head)
    elif algo == "CLOOK":
        return clook(queue, head)

def plot_and_save(path, algo):
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_xlim(-1, len(path) + 1)
    ax.set_ylim(min(path) - 10, max(path) + 10)
    ax.set_title(algo)
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Track Number")
    line, = ax.plot([], [], marker='o', color='royalblue', lw=2)

    def init():
        line.set_data([], [])
        return line,

    def animate(i):
        line.set_data(range(i + 1), path[:i + 1])
        return line,

    ani = FuncAnimation(fig, animate, frames=len(path), init_func=init, interval=500, blit=True)
    gif_path = f"{algo}_animation.gif"
    ani.save(gif_path, writer=PillowWriter(fps=2))
    return gif_path

# --- Simulation Section ---
if simulate:
    queue = list(map(int, queue_input.split(",")))
    path, total_seek = get_result(algo, queue, head)
    gif = plot_and_save(path, algo)
    with open(gif, "rb") as f:
        st.subheader(f"📊 {algo} Disk Scheduling Result")
        st.image(f.read(), caption="Disk Scheduling Animation")
    os.remove(gif)

    st.markdown(f"### ✅ Total Seek Time: `{total_seek}`")
    with st.expander("🔍 Click to see how Seek Time was calculated"):
        st.text(get_seek_explanation(path))

# --- Comparison Section ---
if compare:
    queue = list(map(int, queue_input.split(",")))
    col1, col2 = st.columns(2)

    path1, seek1 = get_result(algo1, queue, head)
    path2, seek2 = get_result(algo2, queue, head)

    gif1 = plot_and_save(path1, algo1)
    gif2 = plot_and_save(path2, algo2)

    with col1:
        st.subheader(f"🔹 {algo1}")
        with open(gif1, "rb") as f1:
            st.image(f1.read(), caption=f"{algo1} Animation")
        st.markdown(f"**✅ Seek Time: `{seek1}`**")
        with st.expander("🔍 See Calculation"):
            st.text(get_seek_explanation(path1))

    with col2:
        st.subheader(f"🔸 {algo2}")
        with open(gif2, "rb") as f2:
            st.image(f2.read(), caption=f"{algo2} Animation")
        st.markdown(f"**✅ Seek Time: `{seek2}`**")
        with st.expander("🔍 See Calculation"):
            st.text(get_seek_explanation(path2))

    os.remove(gif1)
    os.remove(gif2)
