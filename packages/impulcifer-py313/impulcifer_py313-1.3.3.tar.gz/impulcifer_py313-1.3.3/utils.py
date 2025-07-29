# -*- coding: utf-8 -*-

import os
import numpy as np
import soundfile as sf
from scipy.fft import fft, rfft
from scipy import signal
from PIL import Image
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt

plt.rcParams['axes.unicode_minus'] = False


def to_db(x):
    """Convert amplitude to dB

    Args:
        x: Amplitude value

    Returns:
        Value in dB
    """
    return 20 * np.log10(np.abs(x) + 1e-10)


def db_to_gain(x):
    """Convert dB to amplitude gain

    Args:
        x: Value in dB

    Returns:
        Amplitude gain
    """
    return 10 ** (x / 20)


def convolve(x, y):
    """Convolve two signals

    Args:
        x: First signal
        y: Second signal

    Returns:
        Convolved signal
    """
    return signal.convolve(x, y, mode='full')


def dB_unweight(x):
    """Remove dB weighting from a signal

    Args:
        x: Signal with dB weighting

    Returns:
        Signal without dB weighting
    """
    return 10 ** (x / 20)


def read_wav(file_path, expand=False):
    """Reads WAV file

    Args:
        file_path: Path to WAV file as string
        expand: Expand dimensions of a single track recording to produce 2-D array?

    Returns:
        - sampling frequency as integer
        - wav data as numpy array with one row per track, samples in range -1..1
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f'File in path "{os.path.abspath(file_path)}" does not exist.')
    data, fs = sf.read(file_path)
    if len(data.shape) > 1:
        # Soundfile has tracks on columns, we want them on rows
        data = np.transpose(data)
    elif expand:
        data = np.expand_dims(data, axis=0)
    return fs, data


def write_wav(file_path, fs, data, bit_depth=32):
    """Writes WAV file."""
    if bit_depth == 16:
        subtype = "PCM_16"
    elif bit_depth == 24:
        subtype = "PCM_24"
    elif bit_depth == 32:
        subtype = "PCM_32"
    else:
        raise ValueError('Invalid bit depth. Accepted values are 16, 24 and 32.')
    if len(data.shape) > 1 and data.shape[1] > data.shape[0]:
        # We have tracks on rows, soundfile want's them on columns
        data = np.transpose(data)
    sf.write(file_path, data, samplerate=fs, subtype=subtype)


def magnitude_response(x, fs):
    """Calculates frequency magnitude response

    Args:
        x: Input signal
        fs: Sampling rate

    Returns:
        - Frequency values as numpy array
        - Frequency magnitudes as numpy array
    """
    # Use rfft for real-valued signals (more efficient than fft)
    X = rfft(x)
    # Magnitude in dB
    X_mag = 20 * np.log10(np.abs(X) + 1e-10)
    # Frequencies (positive only)
    f = np.arange(len(X)) * fs / (2 * len(X))
    return f, X_mag


def sync_axes(axes, sync_x=True, sync_y=True):
    """Synchronizes X and Y limits for axes

    Args:
        axes: List Axis objects
        sync_x: Flag depicting whether to sync X-axis
        sync_y: Flag depicting whether to sync Y-axis

    Returns:

    """
    x_min = []
    x_max = []
    y_min = []
    y_max = []
    for ax in axes:
        x_min.append(ax.get_xlim()[0])
        x_max.append(ax.get_xlim()[1])
        y_min.append(ax.get_ylim()[0])
        y_max.append(ax.get_ylim()[1])
    xlim = [np.min(x_min), np.max(x_max)]
    ylim = [np.min(y_min), np.max(y_max)]
    for ax in axes:
        if sync_x:
            ax.set_xlim(xlim)
        if sync_y:
            ax.set_ylim(ylim)


def get_ylim(x, padding=0.1):
    lower = np.min(x)
    upper = np.max(x)
    diff = upper - lower
    lower -= padding * diff
    upper += padding * diff
    return lower, upper


def versus_distance(angle=30, distance=3, breadth=0.148, ear='primary', sound_field='reverberant', sound_velocity=343):
    """Calculates speaker-ear distance delta, dealy delta and SPL delta

    Speaker-ear distance delta is the difference between distance from speaker to middle of the head and distance from
    speaker to ear.

    Dealy delta is the time it takes for sound to travel speaker-ear distance delta.

    SPL delta is the sound pressure level change in dB for a distance delta.

    Sound pressure attenuates by 3 dB for each distance doubling in reverberant room
    (http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.10.1442&rep=rep1&type=pdf).

    Sound pressure attenuates by 6 dB for each distance doubling in free field and does not attenuate in diffuse field.

    Args:
        angle: Angle between center and the speaker in degrees
        distance: Distance from speaker to the middle of the head in meters
        breadth: Head breadth in meters
        ear: Which ear? "primary" for same side ear as the speaker or "secondary" for the opposite side
        sound_field: Sound field determines the attenuation over distance. 3 dB for "reverberant", 6 dB for "free"
                     and 0 dB for "diffuse"
        sound_velocity: The speed of sound in meters per second

    Returns:
        - Distance delta in meters
        - Delay delta in seconds
        - SPL delta in dB
    """
    if ear == 'primary':
        aa = (90 - angle) / 180 * np.pi
    elif ear == 'secondary':
        aa = (90 + angle) / 180 * np.pi
    else:
        raise ValueError('Ear must be "primary" or "secondary".')
    b = np.sqrt(distance ** 2 + (breadth / 2) ** 2 - 2 * distance * (breadth / 2) * np.cos(aa))
    d = b - distance
    delay = d / sound_velocity
    spl = np.log(b / distance) / np.log(2)
    if sound_field == 'reverberant':
        spl *= -3
    elif sound_field == 'free':
        spl *= -6
    elif sound_field == 'diffuse':
        spl *= -0
    else:
        raise ValueError('Sound field must be "reverberant", "free" or "diffuse".')
    return d, delay, spl


def optimize_png_size(file_path, n_colors=60):
    """Optimizes PNG file size in place.

    Args:
        file_path: Path to image
        n_colors: Number of colors in the PNG image

    Returns:
        None
    """
    im = Image.open(file_path)
    im = im.convert('P', palette=Image.ADAPTIVE, colors=n_colors)
    im.save(file_path, optimize=True)


def save_fig_as_png(file_path, fig, n_colors=60):
    """Saves figure and optimizes file size."""
    fig.savefig(file_path, bbox_inches='tight')
    optimize_png_size(file_path, n_colors=n_colors)


def config_fr_axis(ax):
    """Configures given axis instance for frequency response plots."""
    ax.set_xlabel('Frequency (Hz)')
    ax.semilogx()
    ax.set_xlim([20, 20e3])
    ax.set_ylabel('Amplitude (dB)')
    ax.grid(True, which='major')
    ax.grid(True, which='minor')
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.0f}'))


def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)
