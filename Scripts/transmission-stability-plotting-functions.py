import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.ndimage import gaussian_filter1d
import scipy.constants as _con

c = _con.c  # speed of light (m/s)

def um2ghz(lamb_um): # converstion functions
    return c / (lamb_um * 1e-6) / 1e9

def ghz2um(freq_ghz):
    return c / (freq_ghz * 1e9) * 1e6

def load_data(filepath): # load data
    return np.loadtxt(filepath, skiprows=1)

def get_amplitude(data, freq, apply_filter=False, sigma=200): # extracts and interpolates amplitude over the given frequency range
    f_data = data[:, 1] # frequency column
    amp_data = data[:, 2] # amplitude column
    f_data, indices = np.unique(f_data, return_index=True)
    amp_data = amp_data[indices]
    interp_func = interpolate.interp1d(f_data, amp_data, kind='cubic', bounds_error=False, fill_value="extrapolate")
    amplitude = interp_func(freq)
    if apply_filter:
        amplitude = gaussian_filter1d(amplitude, sigma)
    return amplitude

def get_phase(data, freq): # extracts and interpolates phase over the given frequency range
    f_data = data[:, 1]
    phase_data = data[:, 3]
    f_data, indices = np.unique(f_data, return_index=True)
    phase_data = phase_data[indices]
    interp_func = interpolate.interp1d(f_data, phase_data, kind='cubic', bounds_error=False, fill_value="extrapolate")
    phase = interp_func(freq)
    return phase

def plot_transmission(ref_path, sample_paths, title='Transmission spectrum', sample_labels=None, apply_filter=False, sigma=200, freq_start = None, freq_end = None):
    """
    Plots the transmission spectrum with an option to apply Gaussian filtering.

    Parameters:
    - ref_path: str, path to reference file
    - sample_paths: list of str, paths to sample measurement files
    - title: str, title of the plot
    - sample_labels: list of str, labels for each sample measurement
    - apply_filter: bool, whether to apply Gaussian filtering
    - sigma: int, smoothing parameter for Gaussian filtering
    - freq_start: float, start frequency for the plot
    - freq_end: float, end frequency for the plot
    """

    ref = load_data(ref_path) #load data
    sample_data = [load_data(path) for path in sample_paths]

    #define frequency range
    if freq_start is not None and freq_end is not None:
        freq = np.linspace(freq_start, freq_end, len(ref))
    else:
        freq_min = max(np.min(ref[:, 1]), min(np.min(s[:, 1]) for s in sample_data))
        freq_max = min(np.max(ref[:, 1]), max(np.max(s[:, 1]) for s in sample_data))
        freq = np.linspace(freq_min, freq_max, len(ref))

    #get amplitude spectra
    ref_amp = get_amplitude(ref, freq, apply_filter, sigma)
    sample_amps = [get_amplitude(sample, freq, apply_filter, sigma) for sample in sample_data]

    #get phase spectra
    ref_phase = get_phase(ref, freq)
    sample_phases = [get_phase(sample, freq) for sample in sample_data]

    #compute transmission
    transmissions = []
    complex_transfer_functions = []

    for i in range(len(sample_data)):
        transmission = (sample_amps[i] / ref_amp) ** 4
        phase_diff = sample_phases[i] - ref_phase
        complex_transfer_function = (sample_amps[i] / ref_amp) * np.exp(1j * phase_diff)
        transmissions.append(transmission)
        complex_transfer_functions.append(complex_transfer_function)

    #plot
    fig, ax1 = plt.subplots(figsize=(8, 5))
    if sample_labels is None: #assign default labels if none provided
        sample_labels = [f"Sample {i+1}" for i in range(len(sample_paths))]

    for transmission, label in zip(transmissions, sample_labels):
        ax1.plot(freq, transmission, label=label)

    ax1.set_xlabel('Frequency [GHz]')
    ax1.set_ylabel('Transmission')
    ax1.set_yscale('log')
    ax1.legend()
    ax1.set_title(title)
    plt.show()

def plot_stability_ratio(air_bf, air_af, title='Air Reference Stability', freq_start = None, freq_end = None):
    """
    Plots the stability of the air reference data (air1/air2)

    Parameters:
    - air_bf: str, path to reference file taken before taking data
    - air_af: list of str, path to reference file taken after taking data
    - title: str, title of the plot
    - freq_start: float, start frequency for the plot
    - freq_end: float, end frequency for the plot
    """

    air_bf = load_data(air_bf)
    air_af = load_data(air_af)

    #define frequency range
    if freq_start is not None and freq_end is not None:
        freq = np.linspace(freq_start, freq_end, len(air_bf))
    else:
        freq = np.linspace(np.min(air_bf[:, 1]), np.max(air_bf[:, 1]), len(air_bf))

    air_bf_amp = get_amplitude(air_bf, freq)
    air_af_amp = get_amplitude(air_af, freq)

    air_ratio = air_af_amp / np.where(air_bf_amp == 0, np.nan, air_bf_amp)

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(freq, air_ratio)
    ax1.axhline(1, linestyle='--', color='black', linewidth=1)
    ax1.set_xlabel('Frequency [GHz]')
    ax1.set_ylabel('Amplitude Ratio')
    ax1.set_title(title)
    plt.ylim(0, 5)
    plt.show()

def plot_stability_diff(air_bf, air_af, title='Air Reference Stability (difference)', freq_start = None, freq_end = None):
    """
    Plots the stability of the air reference data (air1/air2)

    Parameters:
    - air_bf: str, path to reference file taken before taking data
    - air_af: list of str, path to reference file taken after taking data
    - title: str, title of the plot
    - freq_start: float, start frequency for the plot
    - freq_end: float, end frequency for the plot
    """

    air_bf = load_data(air_bf)
    air_af = load_data(air_af)

    #define frequency range
    if freq_start is not None and freq_end is not None:
        freq = np.linspace(freq_start, freq_end, len(air_bf))
    else:
        freq = np.linspace(np.min(air_bf[:, 1]), np.max(air_bf[:, 1]), len(air_bf))

    air_bf_amp = get_amplitude(air_bf, freq)
    air_af_amp = get_amplitude(air_af, freq)

    diff_squared = (air_af_amp - air_bf_amp) ** 2

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(freq, diff_squared)
    ax1.set_xlabel('Frequency [GHz]')
    ax1.set_ylabel('Amplitude Difference²')
    ax1.set_yscale('log')
    ax1.set_title(title)
    plt.show()