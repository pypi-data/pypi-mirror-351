# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Ansel Neunzert (2023)
#               Evan Goetz (2023)
#
# This file is part of fscan

import numpy as np
from gpstime import gpstime
from datetime import datetime
# for smarter calendar-based manipulations...
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
from dateutil.tz import tzutc
import argparse
from glob import glob
import os
import re


def datestr_to_datetime(datestr):
    '''
    Accept a string and parse it into a datetime if it fits any of a list of
    formats. Interpret "now" as the moment the program is run.
    '''

    if datestr.lower().endswith("ago"):
        deltastr = datestr[:-3]
        rdelta, _ = deltastr_to_timedelta(deltastr)
        return datetime.utcnow() - rdelta

    if datestr == "now":
        return datetime.utcnow()

    fmts = [
        "%Y-%m-%d-%H:%M:%S",
        "%Y%m%d-%H%M%S",
        "%Y-%m-%d",
        "%Y%m%d",
        "%Y-%m",
        "%Y%m"][::-1]

    for fmt in fmts:
        try:
            dt = datetime.strptime(datestr, fmt)
            return dt
        except Exception:
            pass

    raise ValueError(f"{datestr} is in some format which is not accepted. "
                     f"Accepted formats: {fmts}")


def datetime_to_gps(dt):
    """
    Turn a python datetime object into a GPS time stamp

    Parameters
    ----------
    dt : `datetime`

    Returns
    -------
    int :
        GPS time
    """
    dt = dt.replace(tzinfo=tzutc())
    return int(gpstime.fromdatetime(dt).gps())


def gps_to_datetime(gps):
    """
    Turn an integer GPS time and turn it into a datetime object

    Parameters
    ----------
    gps : `int`, `float`
        GPS time

    Returns
    -------
    `datetime` :
    """
    return gpstime.fromgps(gps)


def datestr_to_gps(datestr):
    '''
    Small utility function that just sticks together two other functions.
    '''
    dt = datestr_to_datetime(datestr)
    return datetime_to_gps(dt)


def deltastr_to_timedelta(deltastr):
    '''
    Takes a string and parses it into a time interval (specifically a
    *relativetimedelta*, not a regular timedelta). Also returns a neatly
    formatted tag for use in epoch naming, if needed.

    Examples of valid input strings might include "1week", "36hours", "1h30m",
    and many more. You can use abbreviations or not, can use plurals or not.
    When using abbreviations "m" means "minute" and "M" means "month".
    '''

    # setting up some abbreviations
    # this will also be helpful later for validating the input
    shortcuts = {
        'M': 'months',
        'w': 'weeks',
        'd': 'days',
        'h': 'hours',
        'm': 'minutes',
        's': 'seconds',
        }

    # This breaks the input up into sub-strings ("blocks"). It breaks whenever
    # it finds something numeric following something non-numeric.
    # example: "1hour30m" goes to ["1hour","30m"]

    argstring = ""
    blocks = []
    for i in range(len(deltastr)):
        if (deltastr[i].isnumeric() and i != 0 and not
                deltastr[i-1].isnumeric()):
            blocks += [argstring]
            argstring = deltastr[i]
        else:
            argstring += deltastr[i]
    blocks += [argstring]

    # Having broken it up into blocks, we then separate out the numeric and
    # non-numeric parts of each block, creating a dict (td_args) of arguments.
    # Since `td_args` will be used as input to `relativedelta`, we also fix up
    # the dictionary so that all the keys will be valid arguments for
    # `relativedelta`.
    # example: ["1hour","30m"] goes to {"hours":1,"minutes":30}

    td_args = {}
    for block in blocks:
        for i in range(len(block)):  # look through the block
            # when the numeric part ends, we found the splitting point
            if not block[i].isnumeric():
                k = block[i:]
                a = block[:i]
                if k in shortcuts.keys():  # check for abbreviations
                    k = shortcuts[k]
                # check for singular instead of plural
                elif k.lower()+"s" in shortcuts.values():
                    k = k.lower()+"s"
                    if a == '':
                        a = 1
                # check for nonsense
                # TODO: is this logic correct? the last and seems weird
                elif (len(k) == 0 or len(a) == 0 or
                      k not in shortcuts.keys() and
                      k.lower() not in shortcuts.values()):
                    raise ValueError(f"\n\'{deltastr}\' is in some format "
                                     "which is not accepted. In particular, "
                                     f"\'{block}\' cannot be parsed.")
                td_args[k] = int(a)  # turn the numeric part into an int
                break

    # In some special cases we might like to reformat things to look pretty
    # and fit with the standard Fscan naming scheme. This info can be used for
    # epoch naming later.
    # example: "1weeks" goes to "week".

    # In non-special cases, we just save the ugly looking tag.
    # TODO: force "30minutes1hour" to reformat into "1hour30minutes".
    tag = ""
    for v in shortcuts.values():
        if v in td_args.keys():
            tag += f"{td_args[v]}{v}"
    remap = {"1days": "day",
             "1weeks": "week",
             "7days": "week",
             "24hours": "day",
             "1months": "month"}
    if tag in remap.keys():
        tag = remap[tag]

    # return the timedelta and also a human-readable formatted tag describing
    # it.
    return relativedelta(**td_args), tag


def snap_to_midnight(dt):
    '''
    Accept a timedelta and "snap" to the most recent UTC midnight.
    '''
    return dt + relativedelta(hour=0, minute=0, second=0)


def snap_to_day(dt, day, daysDict):
    '''
    Accept a timedelta (datetime object), a string which contains a day of the
    week, and a dictionary of days:relativedelta objects i.e. "tuesday":TU(-1).
    Snaps to the most recent occurrence of that day of the week e.g. Wednesday.
    Note: doesn't change the hour/minute/second, use with snap_to_midnight if
    you want that!
    '''
    # iterate through dictionary of days to match correct argument for
    # relativedelta, {"monday":MO(-1) ...}
    for key in daysDict:
        if (key in day):
            return dt + relativedelta(weekday=daysDict[key])


def snap_to_monthstart(dt):
    '''
    Accept a timedelta and "snap" to the start of the most recent month.
    Note: doesn't change the hour/minute/second, use with snap_to_midnight if
    you want that!
    '''
    return dt + relativedelta(day=1)


def subfolder_format(durationtag, t):
    # if we're starting at UTC midnight on the 1st of the month and we're
    # doing a monthly average
    if ((t.second == 0 and t.minute == 0 and t.hour == 0 and t.day == 1) and
            durationtag == "month"):
        intervaltag = t.strftime("%Y%m")  # label with month only
    # if we're starting at UTC midnight and in a mode that doesn't care about
    # hour/min/sec
    elif (t.second == 0 and t.minute == 0 and t.hour == 0) and all(
            [x not in durationtag for x in ["hour", "minute", "second"]]):
        intervaltag = t.strftime("%Y%m%d")  # label with date only
    else:
        intervaltag = t.strftime("%Y%m%d-%H%M%S")  # otherwise label time
    return intervaltag


def args_to_intervals(args):
    '''
    This is the real important part: it takes all the input arguments and
    computes GPS time intervals, as well as a list of epoch labels in
    duration/starttime format.
    '''
    # small step setting up for iteration
    vargs = vars(args)

    # make sure we have exactly 2 pieces of info for the over all start and end
    # time
    analysisSpanArgs = ['analysisStart', 'analysisEnd', 'analysisDuration']
    if sum(vargs[x] is not None for x in analysisSpanArgs) != 2:
        raise Exception("Must specify exactly 2 of analysisStart, analysisEnd,"
                        " analysisDuration")

    # turn the start and end arguments into datetimes
    if vargs['analysisStart']:
        analysisStart = datestr_to_datetime(vargs['analysisStart'])
    if vargs['analysisEnd']:
        analysisEnd = datestr_to_datetime(vargs['analysisEnd'])

    # Turn the durations into timedeltas
    # noting that analysisDuration might not always be specified (if we got
    # start and end instead) and also that only care about the epoch tag for
    # averageDuration
    averageDuration, durationtag = deltastr_to_timedelta(
        args.averageDuration)
    if args.analysisDuration:
        analysisDuration, _ = deltastr_to_timedelta(
            args.analysisDuration)

    # If we did get analysisDuration, use it to compute start or end
    # After this, we should be done with analysisDuration
    if args.analysisDuration:
        if args.analysisStart:
            analysisEnd = analysisStart + analysisDuration
        elif args.analysisEnd:
            analysisStart = analysisEnd - analysisDuration
    if (analysisEnd) < (analysisStart + averageDuration):
        raise Exception(
            "The averaging duration is too long for the analysis period."
            " The first averaging interval would end on"
            f" {args.analysisStart + args.averageDuration},"
            f" while the full analysis would end on {args.analysisEnd}.")

    # ignore capitals in the snapToLast argument
    args.snapToLast = args.snapToLast.lower()

    # dictionary of days:relativedelta for snap_to_day()
    days = {"monday": MO(-1),
            "tuesday": TU(-1),
            "wednesday": WE(-1),
            "thursday": TH(-1),
            "friday": FR(-1),
            "saturday": SA(-1),
            "sunday": SU(-1)}

    # if the user said to snap, do the thing
    if "month" in args.snapToLast:
        analysisStart = snap_to_monthstart(analysisStart)
    # snap to day if a day is in args.snapToLast
    for i, (day, _) in enumerate(days.items()):
        if (day in args.snapToLast):
            analysisStart = snap_to_day(
                analysisStart, args.snapToLast, days)
    if "midnight" in args.snapToLast:
        analysisStart = snap_to_midnight(analysisStart)
    if args.snapToLast and args.analysisDuration:
        analysisEnd = analysisStart + analysisDuration

    # If the (end-start)/interval isn't an integer, we'll need to decide
    # whether to end early, or whether to be "greedy".
    # quitpoint will tell us where to break a loop shortly.
    if args.greedy:
        quitpoint = analysisEnd
    else:
        quitpoint = analysisEnd - averageDuration

    # set up the lists we want to append to
    gps_intervals = []
    durationtags = []
    intervaltags = []

    # initialize the time
    t = analysisStart

    # start looping
    while t <= quitpoint:
        if t == quitpoint and args.greedy:
            break
        intervaltags += [subfolder_format(durationtag, t)]
        durationtags += [durationtag]

        # get the GPS times for this interval
        intervalStart = datetime_to_gps(t)
        t += averageDuration
        intervalEnd = datetime_to_gps(t)

        gps_intervals += [(intervalStart, intervalEnd)]  # save the GPS times

        # Issue a warning if the 'greedy' argument made us go into the future.
        # Not an exception, though - it wouldn't be ridiculous to set up a
        # future run for testing.
        if intervalEnd > datetime_to_gps(datetime.utcnow()):
            print("\n***Careful! The last calculated interval extends into "
                  "the future.***")

    return gps_intervals, durationtags, intervaltags


def find_specific_SFT(sftname, parentDir, channel, mode=None, exclude=None):
    parentDir = os.path.abspath(parentDir)

    SFTgpsStart = int(sftname.split('-')[-2])
    SFTgpsEnd = SFTgpsStart + int(sftname.split('-')[-1].replace('.sft', ''))
    SFTstart = gps_to_datetime(SFTgpsStart)
    SFTend = gps_to_datetime(SFTgpsEnd)

    chformat = channel.replace(":", "_")

    avgDurFolders = glob(os.path.join(parentDir, "*/"))
    avgDurs = [x.split("/")[-2] for x in avgDurFolders]

    if mode == 'daily-first' and 'day' in avgDurs:
        avgDurs.remove('day')
        avgDurs.insert(0, 'day')
    elif mode == 'daily-only':
        assert 'day' in avgDurs
        avgDurs = ['day']

    # Exclude searching in any average durations listed in exclude
    if exclude is None:
        exclude = []
    for ex in exclude:
        try:
            avgDurs.remove(ex)
        except ValueError:
            pass

    for avgDur in avgDurs:
        try:
            avgDurDt, _ = deltastr_to_timedelta(avgDur)
        except Exception:
            continue
        earliestAvgEnd = subfolder_format(avgDur, SFTend - avgDurDt)
        latestAvgEnd = subfolder_format(avgDur, SFTstart)

        epochFolders = glob(os.path.join(
            parentDir,
            avgDur,
            "*/"))
        epochFolders = np.sort([x.split("/")[-2] for x in epochFolders])

        startInd = np.searchsorted(epochFolders, earliestAvgEnd)
        endInd = np.searchsorted(epochFolders, latestAvgEnd)+1
        checkfolders = epochFolders[startInd:endInd]
        for checkfolder in checkfolders:
            pattern = os.path.join(
                parentDir,
                avgDur,
                checkfolder,
                chformat,
                "sfts",
                sftname)
            if os.path.exists(pattern):
                return pattern
            elif os.path.exists(nosfts := os.path.join(
                    os.path.dirname(pattern), 'nosfts')):
                return nosfts
            else:
                pass

    # If we haven't found anything then return an empty string
    return ''


def parse_filepath(fpath):
    '''
    Extract metadata from a given file path.
    example: "parentDir/1800s/H1_DMT-ANALYSIS_READY/4hours/20200206-000000/H1_GDS-CALIB_STRAIN"  # noqa

    As much metadata as possible will be returned. If, for example, you supply
    a truncated path like: "parentDir/1800s/H1_DMT-ANALYSIS_READY/4hours"
    There will simply be less information in the output dictionary.
/home/ansel.neunzert/public_html/testing_data_v2/1800s/H1_DMT-ANALYSIS_READY/day/20200201/H1_PEM-CS_MAG_EBAY_LSCRACK_Z_DQ  # noqa

    A list of all the dictionary keys is given below -- it is lengthy.
    The data type and an example are also given.

    NOTE: This list is somewhat outdated because the file structure changed to improve the workflow.
    Now, SUPERDAG.dag can exist in the epoch-folder and makesfts.dag will exist in epoch-folder/frametype folder.
    This script is trying to be both backwards compatible with the old structure and also works with the new structure

    username (str)
        ex.: pulsar
    public-html-folder (str)
        ex.: /home/pulsar/public_html
    parentPath (str)
        ex.: /home/pulsar/public_html/fscan
    Tsft-label (str)
        ex.: 1800s
    Tsft (int)
        ex.: 1800
    Tsft-folder (str)
        ex.: /home/pulsar/public_html/fscan/1800s
    segtype (str)
        ex.: H1:DMT-GRD_ISC_LOCK_NOMINAL
    segtype-folder (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL
    duration-label (str)
        ex.: day
    duration (relativedelta)
        ex.: relativedelta(days=+1)
    duration-folder (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day  # noqa
    epoch-label (str)
        ex.: 20230107
    epoch (datetime)
        ex.: 2023-01-07 00:00:00
    epoch-folder (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day/20230107  # noqa
    html-folder (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/summary/day/20230107  # noqa
    channel-label (str)
        ex.: H1_PEM-EX_ADC_0_19_OUT_DQ
    channel (str)
        ex.: H1:PEM-EX_ADC_0_19_OUT_DQ
    ifo (str)
        ex.: H1
    channel-path (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day/20230107/H1_PEM-EX_ADC_0_19_OUT_DQ  # noqa
    sfts-path (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day/20230107/H1_PEM-EX_ADC_0_19_OUT_DQ/sfts  # noqa
    num-sfts-per-channel (int)
        ex.: 88
    superdag-path (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day/20230107/H1_PEM-EX_ADC_0_19_OUT_DQ/SUPERDAG.dag  # noqa
    sftdag-path (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day/20230107/H1_PEM-EX_ADC_0_19_OUT_DQ/tmpSFTDAGtmp.dag  # noqa
    superdagout-path (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day/20230107/H1_PEM-EX_ADC_0_19_OUT_DQ/SUPERDAG.dag.dagman.out  # noqa
    superdag-exists (bool)
        ex.: True
    superdagout-exists (bool)
        ex.: True
    sftdag-exists (bool)
        ex.: True
    coherence-ref-channel (str)
        ex.: H1:GDS-CALIB_STRAIN
    gpsstart (int)
        ex.: 1357085055
    gpsend (int)
        ex.: 1357171177
    fmin (float)
        ex.: 10.0
    fmin-label (str)
        ex.: 10.0000
    fmax (float)
        ex.: 310.0
    fmax-label (str)
        ex.: 310.0000
    plot-subband (int)
        ex.: 100
    sft-overlap (float)
        ex.: 0.5
    timeaverage-npz-path (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day/20230107/H1_PEM-EX_ADC_0_19_OUT_DQ/fullspect_10.0000_310.0000_1357085055_1357171177_timeaverage.npz  # noqa
    speclong-npz-path (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day/20230107/H1_PEM-EX_ADC_0_19_OUT_DQ/fullspect_10.0000_310.0000_1357085055_1357171177_speclong.npz  # noqa
    spectrogram-npz-path (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day/20230107/H1_PEM-EX_ADC_0_19_OUT_DQ/fullspect_10.0000_310.0000_1357085055_1357171177_spectrogram.npz  # noqa
    coherence-npz-path (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day/20230107/H1_PEM-EX_ADC_0_19_OUT_DQ/fullspect_10.0000_310.0000_1357085055_1357171177_coherence.npz  # noqa
    autolines-complete-path (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day/20230107/H1_GDS-CALIB_STRAIN/autolines_complete.txt  # noqa
    autolines-annotated-path (str)
        ex.: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/day/20230107/H1_GDS-CALIB_STRAIN/autolines_annotated_only.txt  # noqa
    '''

    mdata = {}
    # make sure we have expanded all ~ and . in the file path name
    fpath = os.path.abspath(
        os.path.expanduser(fpath))

    # split it into substrings
    substrs = fpath.split("/")

    # Get some basic information about the user and whether this is in a
    # public_html directory
    mdata['username'] = substrs[2]
    if substrs[3] == "public_html":
        mdata['public-html-folder'] = os.path.join("/", *substrs[0:4])
    # Next, we go backward through the file path levels until we reach
    # something that looks like Tsft, and save the appropriate index
    # (It is important to go backward because the autogenerated path should
    # never have something in it like "12345s" which is not a Tsft. However,
    # the parent path might)

    for iback, substr in enumerate(substrs[::-1]):
        if len(substr) == 0:
            return mdata
        elif substr[-1] == "s" and substr[:-1].isnumeric():
            starti = len(substrs)-iback-1
            break

    # now we can select out the auto-generated part of the path
    autopath = substrs[starti:]

    # and we can start building the metadata dict, using as much info
    # as there is available
    mdata['parentPath'] = os.path.join("/", *substrs[:starti])
    mdata['Tsft-label'] = autopath[0]
    mdata['Tsft'] = int(autopath[0].strip("s"))
    mdata['Tsft-folder'] = os.path.join(mdata['parentPath'], autopath[0])
    ndecs = numdecs(1 / mdata['Tsft'])
    if len(autopath) > 1:
        mdata['segtype'] = autopath[1].replace("_", ":", 1)
        mdata['segtype-folder'] = os.path.join(
            mdata['Tsft-folder'], autopath[1])
    if len(autopath) > 2:
        mdata['duration-label'] = autopath[2]
        mdata['duration'], _ = deltastr_to_timedelta(autopath[2])
        mdata['duration-folder'] = os.path.join(
            mdata['segtype-folder'], autopath[2])
    if len(autopath) > 3:
        mdata['epoch-label'] = autopath[3]
        mdata['epoch'] = datestr_to_datetime(autopath[3])
        mdata['epoch-folder'] = os.path.join(
            mdata['duration-folder'], autopath[3])
        mdata['html-folder'] = os.path.join(mdata['segtype-folder'],
                                            'summary',
                                            mdata['duration-label'],
                                            mdata['epoch-label'])
        mdata['superdag-path'] = os.path.join(mdata['epoch-folder'],
                                              'SUPERDAG.dag')
        mdata['superdagout-path'] = os.path.join(mdata['epoch-folder'],
                                                 'SUPERDAG.dag.dagman.out')
        mdata['superdag-exists'] = os.path.isfile(mdata['superdag-path'])
        mdata['superdagout-exists'] = os.path.isfile(mdata['superdagout-path'])

        # If new format of the file structure (SUPERDAG in epoch folder)
        if mdata['superdag-exists']:
            # Read the superdag file
            with open(mdata['superdag-path'], 'r') as dagfile:
                lines = dagfile.readlines()
            makesftfiles = [line.split()[-1]
                            for line in lines if 'SPLICE' in line]
            mdata['multi-channel-sftdag-paths'] = [f for f in makesftfiles]
            mdata['multi-channel-num-sfts-expected'] = 0
            mdata['multi-channel-num-sfts'] = 0
            mdata['multi-channel-sftdag-exists'] = [
                os.path.exists(f) for f in makesftfiles]

            # Handle the fact that the monthly folders were renamed
            # O4 only
            if (all(~x for x in mdata['multi-channel-sftdag-exists']) and
                    mdata['duration-label'] == "month"):
                for idx, makesftfile in enumerate(makesftfiles):
                    if not mdata['multi-channel-sftdag-exists'][idx]:
                        edited_file = makesftfile.replace(
                            f"month/{mdata['epoch-label']}01",
                            f"month/{mdata['epoch-label']}")
                        if os.path.exists(edited_file):
                            mdata['multi-channel-sftdag-paths'][
                                idx] = edited_file
                            mdata['multi-channel-sftdag-exists'][idx] = True
            mdata['multi-channel-list'] = []
            for idx, e in enumerate(mdata['multi-channel-sftdag-exists']):
                if e:
                    with (open(mdata['multi-channel-sftdag-paths'][idx], 'r')
                          as makesftdag):
                        lines = makesftdag.readlines()
                    sftopts = [
                        line.split('argList="')[-1].split('"')[0]
                        for line in lines if 'VARS MakeSFT' in line]
                    chans = sftopts[0].split(' -N ')[-1].split(
                        ' -F ')[0].replace(':', '_').split(',')
                    mdata['multi-channel-num-sfts-expected'] += (
                        len(chans) * len(sftopts))
                    for chan in chans:
                        if chan not in mdata['multi-channel-list']:
                            mdata['multi-channel-list'].append(chan)
            if len(mdata['multi-channel-list']) != 0:
                for chan in mdata['multi-channel-list']:
                    mdata['multi-channel-num-sfts'] += (
                        len(glob(os.path.join(mdata['epoch-folder'],
                                              chan, 'sfts', '*.sft'))))
                mdata['num-sfts-expected-per-channel'] = int(np.round(
                    mdata['multi-channel-num-sfts-expected'] /
                    len(mdata['multi-channel-list'])))
                mdata['fmin'] = float(
                    re.search('-F (\\d*\\.?\\d*)', sftopts[0]).group(1))
                mdata['fmax'] = mdata['fmin'] + float(
                    re.search('-B (\\d*\\.?\\d*)', sftopts[0]).group(1))
                mdata['sft-overlap'] = float(
                    re.search('-P (\\d?\\.?\\d*)', sftopts[0]).group(1)) or 0
                mdata['fmin-label'] = f"{mdata['fmin']:.{ndecs}f}"
                mdata['fmax-label'] = f"{mdata['fmax']:.{ndecs}f}"
                mdata['gpsstart'] = int(
                    re.search('-s (\\d+)', sftopts[0]).group(1))
                mdata['gpsend'] = int(
                    re.search('-e (\\d+)', sftopts[-1]).group(1))

    if len(autopath) > 4:
        mdata['channel-label'] = autopath[4]
        mdata['channel'] = mdata['channel-label'].replace("_", ":", 1)
        mdata['ifo'] = mdata['channel'].split(":")[0]
        mdata['channel-path'] = os.path.join(mdata['epoch-folder'],
                                             autopath[4])
        assert os.path.isdir(mdata['channel-path'])
        if superdag_exists := os.path.isfile(
                os.path.join(mdata['channel-path'], 'SUPERDAG.dag')):
            mdata['superdag-path'] = os.path.join(mdata['channel-path'],
                                                  'SUPERDAG.dag')
            mdata['superdagout-path'] = os.path.join(mdata['channel-path'],
                                                     'SUPERDAG.dag.dagman.out')
            mdata['superdag-exists'] = superdag_exists
            mdata['superdagout-exists'] = os.path.isfile(
                mdata['superdagout-path'])
            # Read the superdag file
            with open(mdata['superdag-path'], 'r') as dagfile:
                lines = dagfile.readlines()
            makesftfile = [line.split()[-1]
                           for line in lines if 'SPLICE' in line][0]
            mdata['sftdag-path'] = os.path.join(mdata['channel-path'],
                                                makesftfile)
            mdata['sftdag-exists'] = os.path.exists(mdata['sftdag-path'])

            if mdata['sftdag-exists']:
                with open(mdata['sftdag-path'], 'r') as makesftdag:
                    lines = makesftdag.readlines()
                sftopts = [line.split('argList="')[-1].split('"tagstring')[0]
                           for line in lines if 'VARS MakeSFT' in line]
                mdata['num-sfts-expected-per-channel'] = len(sftopts)
                mdata['fmin'] = float(
                    re.search('-F (\\d*\\.?\\d*)', sftopts[0]).group(1))
                mdata['fmax'] = mdata['fmin'] + float(
                    re.search('-B (\\d*\\.?\\d*)', sftopts[0]).group(1))
                mdata['sft-overlap'] = float(
                    re.search('-P (\\d?\\.?\\d*)', sftopts[0]).group(1)) or 0
                mdata['fmin-label'] = f"{mdata['fmin']:.{ndecs}f}"
                mdata['fmax-label'] = f"{mdata['fmax']:.{ndecs}f}"
                mdata['gpsstart'] = int(
                    re.search('-s (\\d+)', sftopts[0]).group(1))
                mdata['gpsend'] = int(
                    re.search('-e (\\d+)', sftopts[-1]).group(1))

        if mdata['superdag-exists']:
            with open(mdata['superdag-path'], 'r') as dagfile:
                lines = dagfile.readlines()

            mdata['sfts-path'] = os.path.join(mdata['channel-path'], "sfts")
            mdata['num-sfts-per-channel'] = len(
                glob(os.path.join(mdata['sfts-path'], "*.sft")))

            cohlines = [line for line in lines if "ChASFTs" in line and
                        mdata['channel-label'] in
                        line.split('--ChBSFTs=')[1].split()[0]]
            postproclines = [line for line in lines
                             if "VARS PostProcess" in line and
                             mdata['channel-label'] in line]
        # If coherence is calculated, extract the ref channel
        # if we didn't calculate coherence, there is noref channel
            if len(cohlines) == 0:
                mdata['coherence-ref-channel'] = None
            elif len(cohlines) != 0:
                cohline = cohlines[0]
                refchannel = cohline.split(
                    "--ChASFTs=")[1].split(" ")[0].split("/")[-3]
                if refchannel[2] != "_":
                    raise Exception(f"\"{refchannel}\" does not appear to be a"
                                    " channel")
                refchannel = refchannel.replace("_", ":", 1)
                mdata['coherence-ref-channel'] = refchannel
            if len(postproclines) == 1:
                postprocline = postproclines[0]
                mdata['plot-subband'] = int(
                    postprocline.split("--plot-sub-band ")[1].replace(
                        "\"", " ").split()[0])
            else:
                raise Exception(f"SUPERDAG.dag contains {len(postproclines)} "
                                f"lines  containing 'VARS PostProcess'; "
                                f"1 expected")

    if 'channel-path' in mdata:
        for npztype in ['timeaverage', 'speclong', 'spectrogram', 'coherence']:
            pattern = os.path.join(
                mdata['channel-path'], f"fullspect_*_{npztype}.npz")
            matches = glob(pattern)
            if len(matches) == 1:
                mdata[f"{npztype}-npz-path"] = matches[0]
            elif len(matches) == 0:
                pass
            else:
                raise Exception(f"Expected 1 file to match pattern {pattern}, "
                                f"found {len(matches)}")
        autoline_path = os.path.join(
            mdata['channel-path'], 'autolines_complete.txt')
        if os.path.isfile(autoline_path):
            mdata['autolines-complete-path'] = autoline_path
        autoline_annot_path = os.path.join(
            mdata['channel-path'], 'autolines_annotated_only.txt')
        if os.path.isfile(autoline_path):
            mdata['autolines-annotated-path'] = autoline_annot_path

    return mdata


def numdecs(res, maxtry=15):
    ''' Small utility function that will determine the appropriate number
    of decimal places to use for a given spectral resolution
    '''
    f = np.arange(0, res*5, res)
    for i in range(maxtry+1):
        test = [f"{j:.{i}f}" for j in f]
        if len(set(test)) == len(test):
            return i
    return maxtry


def add_dtlargs(parser):
    '''
    Parameters
    ----------
    parser: argparse parser

    Returns
    -------
    parser: argparse parser
        with appropriate arguments appended.

    This appends all of the arguments that dateTimeLogic (specifically
    args_to_intervals()) needs to generate a range of epochs. May be used by
    external scripts that call args_to_intervals() or other dateTimeLogic
    functions to avoid rewriting the same arguments.
    '''

    parser.add_argument("--analysisStart", type=str, default=None,
                        help="Start of entire analysis. Specify as YYYYMMDD, "
                             "YYYY-MM-DD, YYYY-MM-DD-HH:mm:SS or some other "
                             "formats I should document.")
    parser.add_argument("--analysisEnd", type=str, default=None,
                        help="End of entire analysis. Same formats as "
                             "analysisStart.")
    parser.add_argument("--analysisDuration", type=str, default=None,
                        help="Duration of entire analysis. Accepts formats "
                             "like '1day','1week','1month','36h', "
                             "'1w3days2h1minute', etc.")
    parser.add_argument("--averageDuration", type=str, default=None,
                        required=True,
                        help="Duration of each interval for averaging. Same "
                             "format as analysisDuration.")
    parser.add_argument("--snapToLast", type=str, default='',
                        help="Currently accepts 'midnight','Wednesday', "
                             "'month', and any combination e.g. "
                             "'midnightWednesday'. Doesn't care about "
                             "capitalization.")
    parser.add_argument("--greedy", default=None,
                        help="If there aren't a round number of "
                             "averageDurations per analysisDuration, compute "
                             "one extra averageDuration interval.")
    return parser


def kwargs_to_args(**kwargs):
    '''
    Simple utility so that key word arguments can be parsed by the
    dateTimeLogic argument parser.

    Arguments
    ---------
    kwargs: key word arguments

    Returns
    -------
    args: namespace
        result of parsing the key word arguments through dateTimeLogic
    '''
    to_parse = []
    for key, val in kwargs.items():
        if val is not None:
            to_parse += [f"--{key}", val]
    parser = argparse.ArgumentParser()
    parser = add_dtlargs(parser)
    args = parser.parse_args(to_parse)
    return args


def metadata_from_folders_in_range(segtype_path, only_channels=[], **kwargs):
    '''
    Parse filepath metadata for all available folders in some
    range of epochs.

    Arguments
    ---------
    segtype_path: str
        Path including parent directory, Tsft, and the segment type
        ex: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/

    only_channels: list
        If you want to restrict only certain channels, supply them here.
        Wildcards (*) may be used.

    kwargs: key word arguments
        These should be supplied as on the dateTimeLogic command line.
        You will need at least averageDuration, and two of the following:
        analysisStart, analysisEnd, analysisDuration

    Returns
    -------
    mdatas: list of dicts
        Contains one metadata dict per channel subfolder that exists.
    '''

    args = kwargs_to_args(**kwargs)
    _, durationtags, epochtags = args_to_intervals(args)
    mdatas = []
    for epochtag in epochtags:
        epochpath = os.path.join(
            segtype_path,
            durationtags[0],
            epochtag)
        if len(only_channels) == 0:
            channelpaths = glob(os.path.join(epochpath, "*"))
        else:
            channelpaths = []
            for ch in only_channels:
                pattern = os.path.join(
                    epochpath, ch.replace(":", "_"))
                channelpaths += glob(pattern)
        channelpaths = [c for c in channelpaths if os.path.isdir(c)]
        channelpaths = [c for c in channelpaths if not c.endswith("logs")]
        channelpaths = [c for c in channelpaths if not c.endswith("SFT_GEN")]

        mdatas += [parse_filepath(c) for c in channelpaths]
    return mdatas


def metadata_where_fields_exist_in_range(segtype_path,
                                         fields,
                                         only_channels=[],
                                         **kwargs):
    '''
    Parse filepath metadata for all available folders in some
    range of epochs, then restrict to cases where the requested metadata fields
    exist. (Good for getting all available npz files of a particular type,
    while ignoring directories that contain no data, for instance.)

    Arguments
    ---------
    segtype_path: str
        Path including parent directory, Tsft, and the segment type
        ex: /home/pulsar/public_html/fscan/1800s/H1_DMT-GRD_ISC_LOCK_NOMINAL/

    fields: list of str
        All the metadata fields required. See documentation for
        parse_filepath()

    only_channels: list
        If you want to restrict only certain channels, supply them here.
        Wildcards (*) may be used.

    kwargs: key word arguments
        These should be supplied as on the dateTimeLogic command line.
        You will need at least averageDuration, and two of the following:
        analysisStart, analysisEnd, analysisDuration

    Returns
    -------
    mdata_keep: list of dicts
        Contains one metadata dict per channel subfolder that meets
        requirements.
    '''

    mdata = metadata_from_folders_in_range(
        segtype_path, only_channels, **kwargs)
    mdata_keep = []
    for m in mdata:
        keep = True
        for field in fields:
            if field not in m.keys():
                keep = False
        if keep:
            mdata_keep += [m]
    return mdata_keep


def main():
    # this is for testing - these arguments
    parser = argparse.ArgumentParser()
    parser = add_dtlargs(parser)
    args = parser.parse_args()

    gps_intervals, durationtags, epochtags = args_to_intervals(args)

    # everything over here is for testing
    # Just as a cross-check, I'm computing the GPS times back into human-
    # readable format using the external tconvert tool, rather than doing it in
    # python

    import subprocess
    for i in range(len(gps_intervals)):
        interval = gps_intervals[i]
        epochtag = epochtags[i]
        durationtag = durationtags[i]
        print(f"{durationtag}/{epochtag}")
        subprocess.call(['lal_tconvert', str(interval[0])])
        subprocess.call(['lal_tconvert', str(interval[1])])
