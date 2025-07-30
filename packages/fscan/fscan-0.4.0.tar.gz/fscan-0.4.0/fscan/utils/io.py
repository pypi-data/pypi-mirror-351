# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Evan Goetz (2023)
#               Ansel Neunzert (2023)
#
# This file is part of fscan

import numpy as np
import os
import yaml


def read_channel_config(chan_opts):
    """
    Helper method in case we needed access to loading the channel yml
    information
    """
    with open(chan_opts) as f:
        ch_info = yaml.safe_load(f)

    return ch_info


def load_spect_from_fscan_npz(fname, freqname=None, dataname=None):
    ''' Load spectrum from a data file. Expects Fscan-like .npz data formats.

    Parameters
    ----------
    fname: string
        Path to file
    freqname: str
        name of frequency array to load from npz
    dataname: str
        name of data array to load from npz

    Returns
    -------
    freq: 1-d numpy array (dtype: float)
        Array of frequencies
    val: 1-d numpy array (dtype: float)
        Array of values associated with frequencies
    '''

    # Make sure the file path is properly formatted
    fname = os.path.abspath(os.path.expanduser(fname))

    # allow_pickle is required to load the metadata, which is a dict
    data = np.load(fname, allow_pickle=True)

    # If no column name was specified, guess one from the Fscan standard names.
    if not freqname:
        freqname = 'f'
        print(f"Attempting to load frequencies from array '{freqname}'")
    if not dataname:
        if fname.endswith("_timeaverage.npz"):
            dataname = 'normpow'
        elif fname.endswith("_speclong.npz"):
            dataname = 'psd'
        else:
            raise Exception(
                "Could not guess name of the values column in the npz file")
        print("Attempting to load values from array '{}'".format(dataname))

    # load the data
    freq = data[freqname]
    val = data[dataname]

    return freq, val


def load_lines_from_linesfile(fname):
    '''
    Load line data from a linesfile. Expects csv data with two entries per row,
    the first being a frequency (float) and the second being a label (which
    cannot include commas)

    Example:

    10.000,First line label
    10.003,Second line label
    ...

    If an .npy file is supplied instead, assume it contains frequencies and
    that there are no labels.

    Parameters
    ----------
    fname: string
        Path to file

    Returns
    -------
    lfreq: 1-d numpy array (dtype: float)
        Array of frequencies
    names: 1-d numpy array (dtype: str)
        strings of names associated with given lines.
    '''

    # Make sure the file path is properly formatted
    fname = os.path.abspath(os.path.expanduser(fname))

    if fname.endswith(".npy"):
        lfreq = np.load(fname)
        names = np.array([""]*len(lfreq))
    else:
        # Load the data
        linesdata = np.genfromtxt(fname, delimiter=",", dtype=str)
        if len(linesdata) == 0:
            print("Linesfile does not contain any data.")
            return [], []
        lfreq = linesdata[:, 0].astype(float)
        names = linesdata[:, 1]

    return lfreq, names


def combarg_to_combparams(combarg, delimiter=","):
    '''
    Very small utility for parsing arguments from the command line to
    comb parameters.

    Parameters
    ----------
    combarg: str
        Format: "<spacing>,<offset>" (or other delimiter if specified)

    delimiter: str
        string expected to separate the spacing and offset

    Returns
    -------
    combsp: float
        comb spacing

    comboff: float
        comb offset
    '''

    if delimiter not in combarg:
        raise Exception(
            f"'{combarg}' is not in correct format to specify a comb.")

    # Grab spacing and offset
    combsp, comboff = combarg.split(delimiter)
    combsp = float(combsp)
    comboff = float(comboff)

    return combsp, comboff
