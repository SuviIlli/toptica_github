import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.ndimage import gaussian_filter1d

def data_read(address, cols = ['Frequency Set (GHz)', 'THz Photocurrent (nA)', 'Frequency Act (GHz)',
       '(Frequency corr. smooth (GHz))', 'Amplitude (via StrMod)',
       'Phase (via StrMod)', 'Offset Fit', 'Offset FFT'], delim = "\t"):
    data = pd.read_csv(address, delimiter=delim)
    data = data[cols]
    return data 

def amp_interp(freqs, amps, freqs_aim): 
    freqs, indices = np.unique(freqs, return_index=True)
    amps = amps[indices]
    interp_func = interpolate.interp1d(freqs, amps, kind='cubic', bounds_error=False, fill_value="extrapolate")
    amplitudes = interp_func(freqs_aim)
    return amplitudes

def smoothen_amps(amps, sig = 30):
    return gaussian_filter1d(smoothen_amps, sigma = sig)

def plot_spectra(freq_data, title, amplitudes = [], num_spectrum = 3, labels = None): #Can use this for power ratios as well
    if len(amplitudes) != num_spectrum:
        raise ValueError("Amplitudes list should contain same number of lists as your num_spectrum")
    if labels != None:
        if len(labels) != len(amplitudes):
            raise ValueError("Number of labels should be same as the number of spectra")
    plt.figure(figsize=(16,12))
    for i in range (0, len(amplitudes)):
        if labels !=None:
            plt.semilogy(freq_data, amplitudes[i], label = labels[i], ls = "--")
        else:
            freq_data, amplitudes[i]
    if labels != None:
        plt.legend(fontsize=14)
    plt.xlabel("Frequency [GHz]", fontsize = 16)
    plt.ylabel(r"Amplitude", fontsize = 16)
    plt.title(title, fontsize = 18)
    plt.xticks(fontsize=12)  
    plt.grid()
    plt.yticks(fontsize=12)
    plt.show()

def power_ratio(sample_amplitudes, reference_amplitudes):
    return (sample_amplitudes/reference_amplitudes)**2

def scan_stability(freqs, stability_amplitudes1, stability_amplitudes2):
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    ax = axes[0]
    ax.scatter(freqs, np.abs(stability_amplitudes1-stability_amplitudes2), s= 3)
    ax.set_title("Difference Stability for air")
    ax.set_xlabel("Frequency [GHz]")
    ax.set_ylabel("Amplitude Difference")
    ax = axes[1]
    ax.scatter(freqs, stability_amplitudes1/stability_amplitudes2, s= 3)
    ax.set_title("Difference Stability for air")
    ax.set_xlabel("Frequency [GHz]")
    ax.set_ylabel("Amplitude Ratio")
    plt.show()