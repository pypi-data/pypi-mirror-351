# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Ansel Neunzert (2023)
#
# This file is part of fscan

import argparse
import os
import numpy as np

from ..utils import io
from . import spectlinetools as slt
from . import linefinder as lf
from . import combfinder as cf


def get_args():

    parser = argparse.ArgumentParser()

    # Arguments for input spectrum
    parser.add_argument("--npz-spectfile", required=True)
    parser.add_argument("--freq-colname", type=str,
                        help="Name of frequencies colum in npz file")
    parser.add_argument("--data-colname", type=str,
                        help="Name of data column in npz file")
    parser.add_argument("--fmin", required=True, type=float,
                        help="Minimum frequency to analyze")
    parser.add_argument("--fmax", required=True, type=float,
                        help="Maximum frequency to analyze")

    # Arguments for auto line identification
    parser.add_argument(
        "--autoline-FAR", type=float, default=0.001,
        help=(
            "(very) approximate target per-bin false alarm rate for"
            " linefinding"))
    parser.add_argument("--autoline-window", type=float, default=0.05,
                        help="window for running statistics in Hz")
    parser.add_argument("--autofound-tag", type=str, default=None,
                        help="A tag to prefix any auto-identified lines")

    # (Alternatively) input custom lines file to use for combfinding
    parser.add_argument(
        "--find-combs-from-list",
        help=(
            "Path to existing line file which contains entries to use as"
            " the starting point for combfinding. Overrides the combfinder's"
            " usual first step of auto-finding peaks."))

    # Arguments to use for annotation
    parser.add_argument(
        "--tracked-list", type=str, default=None, nargs="+",
        help=(
            "File(s) containing a list of lines to consider 'previously"
            " known', i.e. tracked"))
    parser.add_argument(
        "--tracked-tag", type=str, default=None,
        help="A tag to prefix any entries from the tracked list")

    # Arguments to parameterize comb finding
    parser.add_argument(
        "--neighbors", type=int, default=50,
        help="Number of nearest neighbors to compare with for each line")
    parser.add_argument("--requirelen", type=int, default=5,
                        help="Minimum number of required entries in comb")
    parser.add_argument(
        "--tracked-combs", nargs="+",
        help="Additional list of combs to consider 'tracked'")

    # Arguments for saving output
    parser.add_argument("--complete-outfile", type=str, default=None,
                        help="Output file for all auto-found lines")
    parser.add_argument(
        "--annotated-only-outfile", type=str, default=None,
        help="Output file for auto-found lines, only those with labels")
    parser.add_argument(
        "--comblist-outfile-entry-format", type=str,
        help=(
            "Output file for auto-found combs in terms of each"
            " individual tooth."))

    return parser.parse_args()


def main(args=None):
    '''
    This function works with a list of previously tracked lines + the results
    of the linefinder & combfinder code to generate a lines list that contains
    information from both sources in a readable, less-cluttered way.

    It saves two output text files, one of which contains the full line list
    including all auto-found line entries, and the other of which only saves
    lines with some kind of annotation (auto-generated or from tracked list)
    '''

    if args is None:
        args = get_args()

    # =====================
    # spectrum file loading
    # =====================
    sfpath = os.path.abspath(args.npz_spectfile)

    sfreq, sval = io.load_spect_from_fscan_npz(sfpath,
                                               dataname=args.data_colname,
                                               freqname=args.freq_colname)
    sfreq, sval = slt.clip_spect(sfreq, sval,
                                 fmin=args.fmin,
                                 fmax=args.fmax,
                                 islinefile=False)

    # ======================
    # Starting list of lines
    # ======================

    # If lines file was given, load lines from that.
    if args.find_combs_from_list:
        print("Initial line list populating from file.")
        lfpath = os.path.abspath(args.find_combs_from_list)
        lfreq, lname = io.load_lines_from_linesfile(lfpath)
        lfreq, lname = slt.clip_spect(lfreq, lname,
                                      fmin=sfreq[0],
                                      fmax=sfreq[-1],
                                      islinefile=True)
        lname = lname.astype(object)
        print(f"Retained {len(lfreq)} lines after frequency cuts.")
        lloc = slt.match_bins(sfreq, lfreq)

    # Otherwise, auto-identify lines.
    else:
        lloc = lf.peaks(sval, args.autoline_FAR,
                        args.autoline_window/(sfreq[1]-sfreq[0]))
        lname = np.array([""]*len(lloc)).astype(object)
        print(f"Found {len(lloc)} lines in spectral region")

    # ==============================================
    # Pre-process tracked lines and combs annotation
    # ==============================================

    afreq = []
    anames = []

    # Read from tracking list(s)
    if args.tracked_list:
        tfreq = np.array([])
        tnames = np.array([])
        for tracked_list in args.tracked_list:
            tfreq_temp, tnames_temp = io.load_lines_from_linesfile(
                tracked_list)
            tfreq = np.append(tfreq, tfreq_temp)
            tnames = np.append(tnames, tnames_temp)
        tfreq, tnames = slt.clip_spect(tfreq, tnames,
                                       fmin=sfreq[0],
                                       fmax=sfreq[-1],
                                       islinefile=True)
        tnames = [t.replace("NEW", "") for t in tnames]
        # Split out lines and combs from tracking list
        tracked_combs_as_strings = []
        tracked_comb_tags = []
        for i, name in enumerate(tnames):
            if " comb " in (name+" ").lower().replace(";", " "):
                spstr = name.split(";", 1)[0].split()[-1]
                offstr = name.split(";", 1)[1].split()[0]
                tracked_combs_as_strings += [(spstr, offstr)]
                if ("[" == name.strip()[0]) and ("]" in name):
                    tracked_comb_tags += [
                        name.split("[")[1].split("]")[0].strip()]
                elif args.tracked_tag:
                    tracked_comb_tags += [args.tracked_tag]
                else:
                    tracked_comb_tags += [""]
            else:
                afreq += [tfreq[i]]
                anames += [tnames[i]]

        # Recall that we have a tag saved for *each* entry in the tracked
        # lines list. However, what we want is one tag per tracked comb,
        # not one tag per *tooth* of the tracked comb.
        # This picks out the set of unique tracked combs, and also finds
        # the corresponding tag (selects the tag of the first tooth).
        unique_tracked_combs_as_strings = list(set(tracked_combs_as_strings))
        unique_tracked_comb_tags = []
        for ctag in unique_tracked_combs_as_strings:
            unique_tracked_comb_tags += [
                tracked_comb_tags[
                    tracked_combs_as_strings.index(ctag)]]
        tracked_combs = [(float(x[0]), float(x[1]))
                         for x in unique_tracked_combs_as_strings]
    # If no tracking list, skip this step
    else:
        tracked_combs = []

    # If additional tracked combs specified from command line, process those
    if args.tracked_combs:
        for combarg in args.tracked_combs:
            # Get all the frequencies and indices expected in the
            # spectral range
            combsp, comboff = io.combarg_to_combparams(combarg)
            tracked_combs += [(combsp, comboff)]

    # Process annotations
    # If a "tracked lines tag" has been specified, append [<tag>] to any
    # un-tagged entries in the tracked lines list
    aloc = slt.match_bins(sfreq, afreq)
    if args.tracked_tag:
        anames_old = anames[:]
        anames = []
        for aname in anames_old:
            if ("[" != aname.strip()[0]) or ("]" not in aname):
                anames += [f"[{args.tracked_tag}] {aname}"]
            else:
                anames += [aname]

    # Process tracked comb entries
    cf_lloc = lloc[:]
    for ic, comb in enumerate(tracked_combs):
        cfreq, cinds, cnames = slt.combparams_to_labeled_teeth(
            comb[0], comb[1], sfreq, lloc)
        ctag = unique_tracked_comb_tags[ic]
        cnames = np.array(
            [f"[{ctag}] "+cname for cname in cnames])
        # Intersect with line locations to determine which are found here
        refound = np.isin(cinds, cf_lloc)
        refoundfreq = cfreq[refound]
        refoundinds = cinds[refound]
        refoundnames = cnames[refound]
        # Filter "re-found" comb teeth for those in consecutive blocks
        # And reject all corresponding spectral indices
        consecfilter = slt.consecutive_filter_Hz(refoundfreq,
                                                 comb[0], comb[1],
                                                 args.requirelen)
        filterinds = refoundinds[consecfilter]
        filternames = refoundnames[consecfilter]
        if len(filterinds) > 0:
            print(
                f"{len(filterinds)} entries belong to tracked comb"
                f" {comb[0]},{comb[1]}")
        # Filter the line list by the indices to keep
        keep = np.invert(np.isin(cf_lloc, filterinds))
        cf_lloc = cf_lloc[keep]
        aloc = np.append(aloc, filterinds)
        anames = np.append(anames, filternames)

    # ==========
    # Find combs
    # ==========

    foundCombs = cf.find_combs(sfreq, sval, cf_lloc,
                               neighbors=args.neighbors,
                               requirelen=args.requirelen)

    # ==================
    # Annotate line list
    # ==================

    # Append labels from auto-found comb list where relevant
    for comb in foundCombs:

        _, cloc, cnames = slt.combparams_to_labeled_teeth(
            comb[0], comb[1], sfreq, lloc)
        if args.autofound_tag:
            cnames = [f"[{args.autofound_tag}] "+cname for cname in cnames]
        aloc = np.append(cloc, aloc)
        anames = np.append(cnames, anames)

    # If a line has a previous annotation and was auto-identified,
    # combfinder, append the annotation to the auto-identified
    # label for the same location.
    overlap_loc = []
    overlap_name = []
    for i, l in enumerate(lloc):
        if l in aloc:
            appendLabels = anames[aloc == l].tolist()
            for appendLabel in appendLabels:
                if len(lname[i].strip()) == 0:
                    lname[i] = appendLabel
                elif appendLabel.strip() not in lname[i]:
                    overlap_loc += [l]
                    overlap_name += [appendLabel]

    lloc = np.append(lloc, overlap_loc).astype(int)
    lname = np.append(lname, overlap_name)

    # ===========
    # Saving data
    # ===========
    if args.annotated_only_outfile:
        with open(args.annotated_only_outfile, 'w') as f:
            for i in range(len(lloc)):
                if len(lname[i].strip()) > 0:
                    f.write(f"{sfreq[lloc[i]]},{lname[i]}\n")

    if args.complete_outfile:
        with open(args.complete_outfile, 'w') as f:
            for i in range(len(lloc)):
                f.write(f"{sfreq[lloc[i]]},{lname[i]}\n")
