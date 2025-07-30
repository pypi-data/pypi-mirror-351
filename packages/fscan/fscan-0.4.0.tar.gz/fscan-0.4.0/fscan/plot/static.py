# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Evan Goetz (2023)
#               Ansel Neunzert (2023)
#
# This file is part of fscan

import matplotlib as mpl
from matplotlib import pyplot as plt
import os
import glob
import numpy as np
import argparse
from ..utils import dtutils as dtl
import matplotlib.dates as mdates
mpl.use('Agg')


def expected_pngs(targetPath, fmin, fmax, fband, gpsStart, gpsEnd, Tsft,
                  ptype):
    '''
    Arguments
    =========
    targetPath: str/path
        Directory for image output
    fmin, fmax: float
        minimum and maximum frequencies for available data
    fband: int
        frequency bandwidth for plots
    gpsStart, gpsEnd: int
        start and end GPS times for plot naming
    Tsft: int
        SFT length (for determining spectral resolution and decimal places)
    ptype: str
        one of 'coherence', 'timeaverage', 'spectrogram', or 'persist'

    Returns
    =======
    fnames: list of strs
        paths to each expected png file
    bmins: list of floats
        frequency minimum for each band
    bmaxs: list of floats
        frequency maximum for each band
    '''
    ndecs = dtl.numdecs(1/Tsft)
    # set up band minima (bands may be skipped or edited if the spectrum
    # does not start at 0 Hz)
    try_bandmins = np.arange(0, fmax, fband, dtype=int)
    # loop over bands and edit the min/max frequencies based on data
    # availability (skip if no data available)
    fnames = []
    bmins = []
    bmaxs = []
    for try_bandmin in try_bandmins:
        bmin = max(try_bandmin, fmin)
        bmax = min(try_bandmin + fband, fmax)
        if bmax <= bmin:
            continue
        fname = os.path.join(
            targetPath,
            f"{ptype}_{bmin:.{ndecs}f}_{bmax:.{ndecs}f}Hz_{gpsStart}_{gpsEnd}"
            ".png")
        fnames += [fname]
        bmins += [bmin]
        bmaxs += [bmax]

    return fnames, bmins, bmaxs


def make_all_plots(targetPath, bandwidth, ptype):
    ''' This sets up all the plots of a given `ptype`, which can be:
        `coherence`
        `timeaverage` (normalized average power)
        `spectrogram`
        `persist` (persistence)

    This function looks for the appropriate npz files, sets up the
    boundaries for each frequency sub-band, and creates an appropriate
    plot title for each sub-band.

    Then, for each sub-band, it calls
    the appropriate function to actually create the plot.
    '''

    # select the merged npz file
    targetPath = os.path.abspath(targetPath)
    if ptype in ['spectrogram', 'timeaverage', 'coherence']:
        spectpattern = os.path.join(
            targetPath,
            f"fullspect_*_{ptype}.npz")
    elif ptype == 'persist':
        spectpattern = os.path.join(
            targetPath,
            "fullspect_*_speclong.npz")

    # check that one npz file is found
    specfiles = glob.glob(spectpattern)
    if len(specfiles) == 1:
        spect = specfiles[0]
    else:
        raise NameError(f"Expected 1 spect file for plot type {ptype}, found "
                        f"{len(specfiles)}")

    # extract the gps start and gps end time from the npz file name
    gpsStart, gpsEnd = os.path.basename(spect).strip(".npz").split("_")[3:5]

    # extract metadata
    mdata = dtl.parse_filepath(targetPath)

    # convert gps times to dates
    dateStart = dtl.gps_to_datetime(int(gpsStart))
    dateStartLabel = dateStart.strftime("%Y/%m/%d %H:%M:%S")
    dateEnd = dtl.gps_to_datetime(int(gpsEnd))
    dateEndLabel = dateEnd.strftime("%Y/%m/%d %H:%M:%S")

    # extract the channel name
    chname = os.path.basename(targetPath).replace("_", ":", 1)

    # set up the title and y bounds
    # (note that we need extra info, the reference channel, for coherence)
    if ptype == 'coherence':
        refchannel = mdata['coherence-ref-channel']
        title = (f"{chname} coherence with {refchannel} \n {dateStartLabel} to"
                 f" {dateEndLabel} UTC")
        ylim_bounds = [-0.1, 1.1]

    if ptype == 'timeaverage':
        title = (f"Normalized spectrum for {chname}\n {dateStartLabel} to "
                 f"{dateEndLabel} UTC")
        ylim_bounds = [0, 4]

    if ptype == 'spectrogram':
        title = (f"Spectrogram for {chname}\n {dateStartLabel} to "
                 f"{dateEndLabel} UTC")

    if ptype == 'persist':
        title = (f"Line persistence data for {chname}\n {dateStartLabel} to "
                 f"{dateEndLabel} UTC")
        ylim_bounds = [-0.1, 1.1]
    # load the data
    data = np.load(spect)
    if ptype == 'coherence':
        f = data['f']
        val = data['coh']
    if ptype == 'timeaverage':
        f = data['f']
        val = data['normpow']
    if ptype == 'spectrogram':
        t = data['gpstimes']
        f = data['f']
        val = data['vals']
    if ptype == 'persist':
        f = data['f']
        val = data['persist']

    # count the number of SFTs
    # TODO: this might not be the best option if we need to regenerate plots
    # after the SFTs have been deleted for space saving...
    numSFTs = len(glob.glob(os.path.join(targetPath, "sfts/*")))

    # construct sub-bands and filenames
    pngnames, pngfmins, pngfmaxs = expected_pngs(
        targetPath,
        mdata['fmin'], mdata['fmax'], bandwidth,
        gpsStart, gpsEnd, mdata['Tsft'],
        ptype)

    for i, fname in enumerate(pngnames):
        # Note: this is not strictly following the half open interval
        # standard of lalsuite tools
        keep_range = np.where((f >= pngfmins[i]) & (f <= pngfmaxs[i]))[0]

        if ptype in ['coherence', 'timeaverage', 'persist']:
            make_timeavg_plot(
                fname,
                title,
                f[keep_range],
                val[keep_range],
                numSFTs,
                ylim_bounds,
                ptype=ptype)
        if ptype == 'spectrogram':
            make_spectrogram(
                fname,
                title,
                t,
                f[keep_range],
                val[keep_range, :],
                mdata['Tsft'],
                dateStart,
                dateEnd)


def make_timeavg_plot(fname, title, f, val, numSFTs, ylim_bounds, ptype):
    # Plot normalized average power vs. frequency
    plt.plot(f, val, '-', linewidth=0.6)

    # Create title, x-axis, and grid (common to both y-scales)
    plt.title(title, fontsize=10)
    plt.xlabel('Frequency (Hz)', fontsize=10)
    plt.locator_params(axis='x', nbins=11)  # limit number of ticks
    plt.xticks(fontsize=9)
    plt.grid(which='both', visible=True)

    # Set up the left-side scale showing normalized average power
    if ptype == 'coherence':
        plt.ylabel('Coherence', fontsize=10)
    if ptype == 'timeaverage':
        plt.ylabel('Normalized Average Power', fontsize=10)
    if ptype == 'persist':
        plt.ylabel('Persistence', fontsize=10)
    plt.yticks(fontsize=9)

    # Set the y-axis limits on the left
    ax1 = plt.gca()
    ax1.set_ylim(ylim_bounds)

    if ptype == 'timeaverage':
        # Now set up the right-side scale showing SNR
        ax2 = ax1.twinx()
        ax2.set_ylabel('SNR', fontsize=10)

        # Make sure the x limits are the same for both sets of axes
        xmin, xmax = ax1.get_xlim()
        ax2.set_xlim(xmin, xmax)

        # Convert the norm. avg. power limits (left) to SNR limits (right)
        ymin2 = (ylim_bounds[0] - 1) * np.sqrt(numSFTs)
        ymax2 = (ylim_bounds[1] - 1) * np.sqrt(numSFTs)
        ax2.set_ylim(ymin2, ymax2)
        ax2.locator_params('y', nbins=11)
        ax2.grid(visible=False)

    # Save normalized average power plot
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()


def make_spectrogram(fname, title, t, f, data, Tsft, dateStart, dateEnd):
    medianv = np.median(data[data > 0])
    minv = np.min(data[data > 0])
    freqres = f[1] - f[0]
    cutoffhigh = medianv + 5*medianv/np.sqrt(freqres*Tsft)
    cutofflow = minv

    cmap = plt.cm.viridis.copy()
    norm = mpl.colors.Normalize(vmin=cutofflow, vmax=cutoffhigh)
    im1 = plt.pcolormesh([dtl.gps_to_datetime(val) for val in t], f, data,
                         norm=norm, cmap=cmap, shading='auto')
    sduration = (dateEnd - dateStart).total_seconds()
    if sduration <= 24*60*60:  # oneday
        hours = mdates.HourLocator(interval=1)
        plt.gca().xaxis.set_major_locator(hours)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    else:
        if sduration <= 31*24*60*60:  # 31 days
            days = mdates.DayLocator(interval=1)
        else:
            days = mdates.DayLocator(interval=5)
        plt.gca().xaxis.set_major_locator(days)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))

    plt.xticks(rotation=90)
    im1.cmap.set_under('#C0C0C0')
    im1.cmap.set_over(cmap.colors[-1])

    plt.title(title, fontsize=10)
    plt.ylabel('Frequency (Hz)', fontsize=10)
    plt.xlabel("UTC time", fontsize=10)
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.grid(visible=False)
    plt.locator_params(axis='y', nbins=11)  # limit number of ticks

    cbar = plt.colorbar(extend='both')
    cbar.set_label('Channel units/root Hz')  # Colorbar label

    plt.tight_layout()
    plt.savefig(fname)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filepath", type=str, required=True,
                        help="filepath of the folder that contains time "
                             "averaged spectrum files")
    parser.add_argument("--bandwidth", type=int, required=True,
                        help="The size of the increments we are dividing the "
                             "frequency range into (Hz). One plot made for "
                             "each increment.")
    args = parser.parse_args()

    make_all_plots(args.filepath, args.bandwidth, ptype='timeaverage')
    make_all_plots(args.filepath, args.bandwidth, ptype='coherence')
    make_all_plots(args.filepath, args.bandwidth, ptype='spectrogram')
    make_all_plots(args.filepath, args.bandwidth, ptype='persist')


if __name__ == "__main__":
    main()
