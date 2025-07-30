# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Ansel Neunzert (2023)
#               Evan Goetz (2023)
#
# This file is part of fscan

import argparse
from glob import glob
import numpy as np
import os
from pathlib import Path

from .plot import finetoothplot, static, linecount
from .process import autotag, linefinder
from .utils import io
from .utils import dtutils as dtl
from .utils.utils import str_to_bool


def convert_fscan_txt_to_npz(parentPathInput, spects, metadata):
    """
    Convert Fscan txt files to npz files

    Parameters
    ----------
    parentPathInput : `str`
        Full path to files
    spects : `str`
        glob-style string for txt files to convert to npz
    metadata: dictionary
        output of dtutils.parse_filepath

    Returns
    -------
    error_num : int
        Return 0 if successful, 1 if data is all zeros or nans

    Raises
    ------
    NameError
        If no files are found with the specified pattern
    """

    patt = os.path.join(parentPathInput, spects)
    files = glob(patt)

    if len(files) == 0:
        raise NameError(f"No files found with pattern {patt}")

    error_num = 0

    for f in files:
        assert f.endswith('txt')

        data = np.transpose(np.loadtxt(f))
        temp_s = f.replace("_H1_", "_").replace(
            "_L1_", "_").strip(".txt")
        temp_s = os.path.basename(temp_s)
        n = temp_s.split("_")
        n[0] = "fullspect"
        n[1] = metadata['fmin-label']
        n[2] = metadata['fmax-label']

        if temp_s.endswith("_PWA"):
            out = os.path.join(
                parentPathInput,
                "_".join(n).replace("_PWA", "_speclongPWA.npz"))
            freq, pwa_tavgwt, pwa_sumwt = data
            if np.all(np.isnan(pwa_tavgwt)):
                error_num = 1
            else:
                np.savez(out,
                         f=freq,
                         pwa_tavgwt=pwa_tavgwt,
                         pwa_sumwt=pwa_sumwt,
                         metadata=metadata)
            del freq, pwa_tavgwt, pwa_sumwt
        elif 'spectrogram' in temp_s:
            out = os.path.join(
                parentPathInput, ".".join(["_".join(n), "npz"]))
            gpstimes = data[0, 1:]
            vals = data[1:, 1:]
            freq = data[1:, 0]
            if np.all(vals == 0):
                error_num = 1
            else:
                np.savez(out,
                         f=freq,
                         vals=vals,
                         gpstimes=gpstimes,
                         metadata=metadata)
            del gpstimes, vals, freq
        elif 'timeaverage' in temp_s:
            out = os.path.join(
                parentPathInput, ".".join(["_".join(n), "npz"]))
            freq, normpow = data
            if np.all(normpow == 0):
                error_num = 1
            else:
                np.savez(out,
                         f=freq,
                         normpow=normpow,
                         metadata=metadata)
            del freq, normpow
        elif 'coh' in temp_s:
            out = os.path.join(
                parentPathInput,
                "_".join(n).replace("_coh", "_coherence.npz"))
            freq, coh = data
            if np.all(np.isnan(coh)):
                error_num = 1
            else:
                np.savez(out,
                         f=freq,
                         coh=coh,
                         metadata=metadata)
            del freq, coh
        elif 'speclong' in temp_s:
            out = os.path.join(
                parentPathInput,
                "".join(["_".join(n), "_speclong.npz"]))
            freq, psd, amppsd, psdwt, amppsdwt, persist = data
            if np.all(psd == 0):
                error_num = 1
            else:
                np.savez(out,
                         f=freq,
                         psd=psd,
                         amppsd=amppsd,
                         psdwt=psdwt,
                         amppsdwt=amppsdwt,
                         persist=persist,
                         metadata=metadata)
            del freq, psd, amppsd, psdwt, amppsdwt, persist

    return error_num


def delete_ascii(parentPathInput, spects):
    """
    Delete Fscan txt files

    Parameters
    ----------
    parentPathInput : `str`
        Full path to files
    spects : `str`
        glob-style string for txt files to delete

    Raises
    ------
    NameError
        If no files are found with the specified pattern
    """
    patt = os.path.join(parentPathInput, spects)
    files = glob(patt)

    if len(files) == 0:
        raise NameError(f"No files found with pattern {patt}")

    for f in files:
        assert f.endswith('txt')

        os.remove(f)


def main():
    parser = argparse.ArgumentParser()
    parser.register('type', 'bool', str_to_bool)
    parser.add_argument("--delete-converted-text", type='bool', default=False)
    parser.add_argument("--parentPathInput", type=str)
    parser.add_argument("--plot-sub-band", type=int, default=100,
                        help="Plot frequency bands are rounded to nearest"
                             " integer of this size")
    parser.add_argument("--LF-emailFrom", type=str, default=None,
                        help="Sender email address for LineForest alerts")
    parser.add_argument("--LF-emailTo", type=str, default=None,
                        help="Recipient email address for LineForest alerts")
    parser.add_argument("--tracked-line-list", type=str, nargs="+",
                        default=None, help="Reference list for line tracking")
    parser.add_argument("--tracked-line-tag", type=str, default=None)
    args = parser.parse_args()

    metadata = dtl.parse_filepath(args.parentPathInput)

    # Make the file path nicer
    args.parentPathInput = os.path.abspath(
        os.path.expanduser(args.parentPathInput))

    # ==============================
    # Save NPZ data for the spectra
    # ==============================
    try:
        errnum1 = convert_fscan_txt_to_npz(
            args.parentPathInput, "spec_*_timeaverage.txt", metadata)
        errnum2 = convert_fscan_txt_to_npz(
            args.parentPathInput, "spec_*_spectrogram.txt", metadata)
        errnum3 = 0
        if len(glob(os.path.join(args.parentPathInput, "spec_*_coh.txt"))) > 0:
            errnum3 = convert_fscan_txt_to_npz(
                args.parentPathInput, "spec_*_coh.txt", metadata)
        # this covers both speclong file outputs
        errnum4 = convert_fscan_txt_to_npz(
            args.parentPathInput, "speclong_*.txt", metadata)
    except NameError as e:
        # check for nosfts file in the SFTs folder
        if os.path.exists(
                os.path.join(args.parentPathInput, 'sfts', 'nosfts')):
            print(f'WARNING: {e}. Found a nosfts file. Exiting.')
            return
        else:
            raise

    if np.any([errnum1, errnum2, errnum3, errnum4]):
        Path(os.path.join(args.parentPathInput, 'sfts', 'zerosfts')).touch()
        print('WARNING: input data is either all zeros or nans. Exiting.')
        return

    # ==========
    # Make plots
    # ==========

    try:
        static.make_all_plots(args.parentPathInput,
                              args.plot_sub_band, ptype='timeaverage')
        static.make_all_plots(args.parentPathInput,
                              args.plot_sub_band, ptype='spectrogram')
        # if coherence data
        if len(glob(os.path.join(args.parentPathInput,
                                 'fullspect_*_coherence.npz'))) > 0:
            static.make_all_plots(args.parentPathInput,
                                  args.plot_sub_band, ptype='coherence')
        # if the spec_avg_long output was generated
        if len(glob(os.path.join(args.parentPathInput,
                                 'fullspect_*_speclong.npz'))) > 0:
            static.make_all_plots(args.parentPathInput,
                                  args.plot_sub_band, ptype='persist')
    except NameError as e:
        # check for nosfts file in the SFTs folder
        if os.path.exists(
                os.path.join(args.parentPathInput, 'sfts', 'nosfts')):
            print(f'WARNING: {e}. Found a nosfts file. Exiting.')
            return
        else:
            raise

    # Special case for strain or delta L channels
    if "STRAIN" in metadata['channel'] or "DELTAL" in metadata['channel']:

        # =====================
        # Line and comb finding
        # =====================

        autoTagArgs = argparse.Namespace(
            npz_spectfile=glob(
                os.path.join(
                    args.parentPathInput,
                    "fullspect*_timeaverage.npz"))[0],
            data_colname='normpow',
            freq_colname='f',
            fmin=metadata['fmin'],
            fmax=metadata['fmax'],
            tracked_list=args.tracked_line_list,
            autofound_tag=None,
            annotated_only_outfile=os.path.join(
                args.parentPathInput,
                "autolines_annotated_only.txt"),
            complete_outfile=os.path.join(
                args.parentPathInput,
                "autolines_complete.txt"),
            find_combs_from_list=None,
            tracked_combs=None,
            tracked_tag=args.tracked_line_tag,
            autoline_FAR=0.001,
            autoline_window=0.05,
            neighbors=50,
            requirelen=5
        )

        autotag.main(autoTagArgs)

        # ==============
        # Line counting
        # ==============

        endpt = (metadata['epoch']+metadata['duration']).strftime(
                "%Y%m%d-%H%M%S")

        linecount_args = argparse.Namespace(
            autolinesType="complete",
            segtypePath=metadata["segtype-folder"],
            fBins=None,
            outfile_heatmap=os.path.join(args.parentPathInput, "heatmap.png"),
            outfile_countplot=os.path.join(
                args.parentPathInput, "linecount.png"),
            channel=metadata['channel'],
            numSFTsCutoff=6,
            dataPtsInHistory=30,
            analysisDuration="3months",
            averageDuration=metadata['duration-label'],
            analysisEnd=endpt,
            analysisStart=None,
            snapToLast='',
            greedy=None,
            )

        linecount.main(linecount_args)

        # ===============================================
        # Interactive plotting - normalized average power
        # ===============================================

        fstep = 300
        for fmin in np.arange(0, metadata['fmax'], fstep):
            ftag = f"{int(fmin):04}to{int(fmin+fstep):04}Hz"
            plotArgs = argparse.Namespace(
                spectfile=autoTagArgs.npz_spectfile,
                spectfile_ref=None,
                fmin=fmin,
                fmax=fmin+fstep,
                outfile=os.path.join(
                    args.parentPathInput,
                    f"visual_overview_{ftag}.html"),
                datacolname='normpow',
                freqcolname='f',
                legend=True,
                title=(
                    f"{metadata['channel']}"
                    f" {metadata['epoch'].strftime('%Y-%m-%d')}"),
                yaxlabel="Normalized average power",
                ylog=True,
                annotate=False,
                linesfile=[autoTagArgs.annotated_only_outfile],
                plotcombs=None,
                intersect_linefinder=False,
                colorcode='autocolor',
                colorcode_group_min=3
            )

            finetoothplot.main(plotArgs)

        # ==================================
        # Interactive plotting - persistence
        # ==================================

        plotArgs = argparse.Namespace(
            spectfile=glob(
                os.path.join(
                    args.parentPathInput,
                    "fullspect*_speclong.npz"))[0],
            spectfile_ref=None,
            fmin=autoTagArgs.fmin,
            fmax=autoTagArgs.fmax,
            outfile=os.path.join(
                args.parentPathInput,
                "visual_overview_persist.html"),
            datacolname='persist',
            freqcolname='f',
            legend=True,
            title=(
                f"{metadata['channel']}"
                f" {metadata['epoch'].strftime('%Y-%m-%d')}"),
            yaxlabel="Persistence",
            ylog=False,
            annotate=False,
            linesfile=[autoTagArgs.annotated_only_outfile],
            plotcombs=None,
            intersect_linefinder=False,
            colorcode='autocolor',
            colorcode_group_min=3
        )

        finetoothplot.main(plotArgs)

    elif (metadata['coherence-ref-channel'] and
          len(glob(os.path.join(
              args.parentPathInput, "fullspect*_coherence.npz")))):
        # ================
        # linefinding only
        # ================
        f, coh = io.load_spect_from_fscan_npz(
            glob(os.path.join(
                args.parentPathInput,
                "fullspect*_coherence.npz"))[0],
            dataname='coh')
        line_locs = linefinder.peaks(coh, 0.001, 0.05/(f[1]-f[0]))
        coh_linefile = os.path.join(
            args.parentPathInput,
            "autolines_complete_coherence.txt")
        with open(coh_linefile, 'w') as cohf:
            for lloc in line_locs:
                cohf.write(f"{f[lloc]},coherence {coh[lloc]}\n")

        # ================================
        # Interactive plotting - coherence
        # ================================

        ref_linesfile = os.path.join(
            metadata['epoch-folder'],
            metadata['coherence-ref-channel'].replace(":", "_"),
            "autolines_annotated_only.txt")
        if not os.path.isfile(ref_linesfile):
            raise Exception(f"Couldn't find line file at {ref_linesfile}")

        plotArgs = argparse.Namespace(
            spectfile=glob(
                os.path.join(
                    args.parentPathInput,
                    "fullspect*_coherence.npz"))[0],
            spectfile_ref=None,
            fmin=0,
            fmax=300,
            outfile=os.path.join(
                args.parentPathInput,
                "visual_overview_coherence.html"),
            datacolname='coh',
            freqcolname='f',
            legend=True,
            title=(
                f"{metadata['channel']}"
                f" {metadata['epoch'].strftime('%Y-%m-%d')}"),
            yaxlabel=f"Coherence with {metadata['coherence-ref-channel']}",
            ylog=False,
            annotate=False,
            linesfile=[ref_linesfile],
            plotcombs=None,
            intersect_linefinder=False,
            colorcode='autocolor',
            colorcode_group_min=3
        )
        print(plotArgs.outfile)

        finetoothplot.main(plotArgs)

    # Finally, delete the txt files if requested
    if args.delete_converted_text:
        delete_ascii(args.parentPathInput, "spec*.txt")

    Path(os.path.join(args.parentPathInput, 'postProcess_success')).touch()
    print("Completed postProcess successfully")


if __name__ == "__main__":
    main()
