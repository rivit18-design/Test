# Streamlit Parametric Animation (single file)
# Preview a frame, animate in-app, and export a GIF.
# Run:
#   pip install -r requirements.txt
#   streamlit run streamlit_app.py

import io
import time
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import streamlit as st

# -----------------------------
# Math and constants
# -----------------------------
# Precompute arrays once
i = np.arange(9999, -1, -1, dtype=np.float64)
x = i.copy()
y = i / 235.0

# Plot range (same as original)
XR = (70, 330)
YR = (30, 350)

def compute_points(t: float):
    """Vectorized port of the original equations."""
    k = (4.0 + np.sin(x / 11.0 + 8.0 * t)) * np.cos(x / 14.0)
    e = y / 8.0 - 19.0
    d = np.sqrt(k * k + e * e) + np.sin(y / 9.0 + 2.0 * t)
    q = 2.0 * np.sin(2.0 * k) + np.sin(y / 17.0) * k * (9.0 + 2.0 * np.sin(y - 3.0 * d))
    c = (d * d) / 49.0 - t
    xp = q + 50.0 * np.cos(c) + 200.0
    yp = q * np.sin(c) + d * 39.0 - 440.0
    # Flip Y as in {xp, 400 - yp}
    X = xp
    Y = 400.0 - yp
    return X, Y

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Parametric Animation", page_icon="🎞️", layout="wide")
st.title("Parametric Animation - Streamlit")

with st.sidebar:
    st.header("Controls")
    t_preview = st.slider("Preview t", 0.0, 2.0 * np.pi, 0.0, 0.005)
    point_size = st.slider("Point size", 0.1, 2.0, 0.6)
    bg_color = st.color_picker("Background", "#090909")
    dot_color = st.color_picker("Dot color", "#FFFFFF")

    st.divider()
    frames = st.slider("Frames", 30, 360, 180, 10)
    fps = st.slider("FPS", 10, 60, 30, 5)

    run_anim = st.button("Animate in app", use_container_width=True)
    export_gif = st.button("Export GIF", use_container_width=True)

# ---------- Preview a single frame ----------
X, Y = compute_points(t_preview)
fig_prev, ax_prev = plt.subplots(figsize=(6, 6), dpi=150)
ax_prev.set_facecolor(bg_color)
ax_prev.scatter(X, Y, s=point_size, c=dot_color, alpha=0.9, edgecolors="none")
ax_prev.set_xlim(*XR)
ax_prev.set_ylim(*YR)
ax_prev.set_xticks([])
ax_prev.set_yticks([])
ax_prev.set_aspect("equal", "box")
st.pyplot(fig_prev, use_container_width=False)

# ---------- Animate live in Streamlit ----------
if run_anim:
    placeholder = st.empty()
    ts = np.linspace(0.0, 2.0 * np.pi, frames, endpoint=True)
    for t in ts:
        X, Y = compute_points(t)
        fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
        ax.set_facecolor(bg_color)
        ax.scatter(X, Y, s=point_size, c=dot_color, alpha=0.9, edgecolors="none")
        ax.set_xlim(*XR)
        ax.set_ylim(*YR)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal", "box")
        placeholder.pyplot(fig)
        time.sleep(max(1e-3, 1.0 / fps))

# ---------- Export as GIF (no ffmpeg required) ----------
def build_animation(fig, scat, ts):
    def init():
        scat.set_offsets(np.empty((0, 2)))
        return (scat,)
    def update(frame_idx):
        t = ts[frame_idx]
        X, Y = compute_points(t)
        scat.set_offsets(np.column_stack([X, Y]))
        return (scat,)
    return FuncAnimation(fig, update, frames=len(ts), init_func=init, blit=True)

if export_gif:
    ts = np.linspace(0.0, 2.0 * np.pi, frames, endpoint=True)
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.set_facecolor(bg_color)
    scat = ax.scatter([], [], s=point_size, c=dot_color, alpha=0.9, edgecolors="none")
    ax.set_xlim(*XR)
    ax.set_ylim(*YR)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal", "box")

    ani = build_animation(fig, scat, ts)

    buf = io.BytesIO()
    writer = PillowWriter(fps=fps)
    ani.save(buf, writer=writer, dpi=150)
    buf.seek(0)
    filename = f"parametric_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gif"
    st.download_button("Download GIF", data=buf, file_name=filename, mime="image/gif")
    st.success("GIF ready. Use the download button above.")
