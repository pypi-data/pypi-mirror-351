# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Ansel Neunzert (2023)
#
# This file is part of fscan

from .spectlinetools import match_bins
import numpy as np
from scipy.optimize import curve_fit

# ------------------------------------------
# Small functions for comb parameter fitting
# ------------------------------------------


def comb_form(n, sp, off):
    '''
    This function returns the frequency of the nth harmonic
    of a comb with spacing `sp` and offset `off'
    (Used for fitting comb parameters)

    Parameters
    ----------
    n: int
        harmonic number
    sp: float
        spacing (Hz)
    off: float
        offset from integer multiples of spacing (Hz)

    Returns
    -------
    frequency: float
        Frequency of nth harmonic
    '''
    return sp*n+off


def comb_form_zero_off(n, sp):
    '''
    This function returns the frequency of the nth harmonic
    of a comb with spacing `sp` and offset zero
    (Used for fitting comb parameters)

    Parameters
    ----------
    n: int
        harmonic number
    sp: float
        spacing (Hz)

    Returns
    -------
    frequency: float
        Frequency of nth harmonic
    '''
    return sp*n

# -------------------------------------------------------------
# Stuff for validating the allowed properties of custom classes
# -------------------------------------------------------------


def validate(validargs, givenargs):
    '''
    Checks a supplied dictionary of arguments against
    a dictionary of valid argument names and types

    Parameters
    ----------
    validargs: dict
        Entries of the form `key: type`

    givenargs: dict
        Entries of the form `key: value`

    Returns
    -------

    out_dict: dict
        Entries of the form `key: value`
        with some appropriate type conversions (e.g. int to float)
    '''

    out_dict = {}
    # iterate over the keyword args supplied
    for kw in givenargs.keys():
        # if it's a valid argument...
        if kw in validargs:
            # if the type is correct, add to output dict
            if isinstance(givenargs[kw], validargs[kw]):
                out_dict[kw] = givenargs[kw]
            # if the type is int, but we expected float,
            # just change int to float and update.
            elif isinstance(givenargs[kw], int) and validargs[kw] is float:
                out_dict[kw] = float(givenargs[kw])
            # if the type is int64 but we expected int, just change it to int
            elif (type(givenargs[kw]).__name__ == 'int64'
                    and validargs[kw] is int):
                out_dict[kw] = int(givenargs[kw])
            # if the type doesn't match at all, raise an exception
            else:
                raise Exception(
                    f"Incorrect type '{type(givenargs[kw]).__name__}' for "
                    f"property '{kw}'; expected '{validargs[kw].__name__}'")
        else:
            raise Exception(f"{kw} is not a valid argument for this class.")
        accept_types = ['list', 'spect', None]
        if kw == 'source_type' and givenargs[kw] not in accept_types:
            raise Exception(f"Source type must be one of {accept_types}")

    return out_dict


def fillnone(validargs, existdict):
    '''
    Fills in an existing dict `existdict` so that it contains all
    the keys in `validargs`, with None as the value
    if the key was not already in `existdict`

    Parameters
    ----------
    validargs: dict
        Entries of the form `key: type`

    existdict: dict
        Entries of the form `key: value`

    Returns
    -------
    existdict: dict
        Modified so that any new keys from `validargs`
        have been added with value `None`
    '''
    for v in validargs:
        if v not in existdict.keys():
            existdict[v] = None
    return existdict


def print_info(existdict):
    '''
    Custom print function for class properties
    '''
    for kw in existdict.keys():
        if kw not in ['validargs', 'members', 'parent']:
            print(f"{kw}: {existdict[kw]}")
        if kw == 'members':
            print(f"[{len(existdict[kw])} members]")
        if kw == 'parent':
            print(f"[contained in {len(existdict[kw])} linelist]")


class customObj:
    '''
    Custom base class which will be used for other objects.
    Mainly just allows me to use the argument validation
    without rewriting it every time.
    '''

    def __init__(self, validargs, kwargs):

        self.__dict__.update(
            validate(
                validargs,
                kwargs))

        self.__dict__.update(
            fillnone(
                validargs,
                self.__dict__))

    def print_info(self):
        print_info(self.__dict__)


# -------------------------------------------------------------
# Here's where we start defining more useful/interesting things
# -------------------------------------------------------------

class Line(customObj):
    ''' The most important property of a line is its frequency;
    it makes no sense to define a line without that.

    The second most important property of a line is the spectrum
    in which it occurs (if specified). An alternate way to specify
    the line frequency is by supplying a spectrum and spectral index.

    Lines may be members of LineLists. At present, each line can
    only have one such parent.

    Lines can also store additional information, like a label, a
    prominence, or a height (the latter currently unused, but included
    for future extensibility).
    '''

    def __init__(self, **kwargs):
        self.validargs = {
            "freq": float,
            "label": str,
            "spectral_index": int,
            "prominence": float,
            "height": float,
            "spectrum": Spectrum,
            "parent": LineList,
        }
        customObj.__init__(self, self.validargs, kwargs)

        # if we weren't given a spectrum, but the parent LineList has one,
        # update the Line spectrum property accordingly.
        if (not self.spectrum) and self.parent:
            if self.parent.spectrum:
                self.spectrum = self.parent.spectrum

        # If we got a frequency and a spectral index, complain since these
        # things could be incompatible; one should be calculated from the other
        if self.freq is not None:
            if self.spectral_index:
                raise Exception(
                    "Please do NOT supply both a frequency and a spectral "
                    "index, as these may conflict.")
        # adjust_to_bin handles the cases where there is a spectral index and
        # a spectrum, or where there is a frequency and we need to get the
        # nearest spectral index
        self.adjust_to_bin()

        # If we still don't have a frequency, raise an exception
        if self.freq is None:
            raise Exception(
                "Line must have a frequency, or enough information "
                "to calculate one")

    def adjust_to_bin(self):
        ''' If there is a spectrum associated with the line, we may wish
        to adjust the frequency of the line to that of the nearest spectral
        bin center.
        '''
        if self.spectrum is None:
            raise Exception(
                "Cannot adjust to bin; no spectrum associated with this line.")

        if self.spectral_index:
            pass
        else:
            self.spectral_index = match_bins(
                self.spectrum.freq_array,
                [self.freq])[0]
        self.freq = self.spectrum.freq_array[self.spectral_index]


class LineList(customObj):

    def __init__(self, **kwargs):
        self.validargs = {
            'label': str,
            'members': list,
            'spectrum': Spectrum,
            'iscomb': bool,
            'combsp': float,
            'comboff': float,
        }
        customObj.__init__(self, self.validargs, kwargs)
        self.members = []

    def append_line(self, line, duplicate_mode='allow', move_quiet=False):

        if not isinstance(line, Line):
            raise Exception("Can only append a Line to a LineList")

        if duplicate_mode == "allow":
            pass
        elif duplicate_mode in ["alert", "skip", "disallow"]:
            for m in self.members:
                if is_equivalent(m, line):
                    if duplicate_mode == "alert":
                        print(
                            f"Warning: added line with frequency {line.freq}"
                            f" is equivalent to line with frequency {m.freq}"
                            f" in LineList '{self.label}'")
                    elif duplicate_mode == "skip":
                        return
                    else:
                        raise Exception(
                            f"Added line with frequency {line.freq} is"
                            f" equivalent to line with frequency {m.freq} in"
                            f" LineList '{self.label} and cannot be added"
                            f" under duplicate mode 'disallow'.")

        # If the line already has a parent, we are effectively moving it.
        if line.parent:
            if not move_quiet:
                print(
                    f"Line can only be a member of one line list. It will be"
                    f" removed from LineList {line.parent.label} so that it"
                    f" can be appended to LineList {self.label}")
            line.parent.members.remove(line)
        # Set the line properties appropriately
        self.members += [line]
        line.parent = self
        # If this LineList is associated with a spectrum,
        # propose associating the line with the same spectrum
        if self.spectrum is not None:
            # If the line already has a spectrum and it's not the
            # same spectrum, raise an exception
            if line.spectrum is not None:
                if line.spectrum != self.spectrum:
                    raise Exception(
                        "Cannot append Line to LineList; "
                        "they have different source spectra.")
            # If the line has no spectrum of its own,
            # associate it with the LineList's spectrum
            line.spectrum = self.spectrum
            line.adjust_to_bin()
        # Sort the lines by frequency
        self.sort_lines()

    def sort_lines(self):
        self.members.sort(key=lambda x: x.freq)

    def print_lines(self):
        for m in self.members:
            print(f"{m.freq},{m.label}")

    def get_frequency_range(self):
        return (self.members[0].freq, self.members[-1].freq)

    def get_all_frequencies(self):
        return [m.freq for m in self.members]

    def get_all_spectral_indices(self):
        return [m.spectral_index for m in self.members]

    def fit_comb_params(self):
        '''
        This function attempts to fit a frequency and offset to current
        members of the LineList, and sets self.iscomb=True if successful
        as well as updating self.combsp and self.comboff.

        Zero offset is tried first, so that it is prioritized over nonzero
        offset.

        In order to be a successful fit, the recovered comb parameters must
        accurately predict the frequency bins of *every* line in the current
        set of LineList members.
        '''
        # grab the frequency information of the current set of lines
        freqs = np.array(self.get_all_frequencies())
        fmin, fmax = self.get_frequency_range()
        frange = fmax-fmin

        # get an extremely rough spacing estimate
        # (only for harmonic calculation)
        approx_sp = min(np.diff(freqs))

        # Calculate harmonic numbers for given peaks.
        # If we allow offset, then we should choose
        # the floor of the frequency/spacing. (Remainder
        # can be described by an offset.)

        # If we hypothesize zero offset, then we should
        # round (closest integer gives best chance of finding
        # a real comb).
        ns_zero_off = np.round(freqs/approx_sp)
        # If we hypothesize nonsero offset, we should take the
        # the floor instead (any deviation from an integer
        # multiple of the spacing can be explained as a
        # positive offset that way)
        ns_with_off = np.floor(freqs/approx_sp)
        nss = [ns_zero_off, ns_with_off]

        # First, attempt a curve fit assuming zero offset.
        # If that doesn't fit, attempt a curve fit with nonzero offset.
        bounds_zero_off = (
            [0, 0],
            [frange, 0])
        bounds_with_off = (
            [0, 0],
            [frange, frange])
        boundss = [bounds_zero_off, bounds_with_off]

        # First try fitting to a comb with zero offset. If that fails,
        # try fitting to a comb with nonzero offset.
        isComb = False
        for iform, form in enumerate(zip(nss, boundss)):
            ns, bounds = form
            try:
                params, _ = curve_fit(comb_form,
                                      ns,
                                      freqs,
                                      bounds=bounds,
                                      method='dogbox')
            except Exception:
                continue
            sp, off = params

            # Check whether the proposed spacing & offset fully describe
            # the given set of lines
            predictedFreqs = ns*sp + off
            predictedLocs = match_bins(
                self.spectrum.freq_array,
                predictedFreqs)

            if np.all(predictedLocs == self.get_all_spectral_indices()):
                isComb = True
                break

        if isComb:
            self.iscomb = True
            self.combsp = sp
            self.comboff = off
        else:
            self.iscomb = False
            self.combsp = None
            self.comboff = None


class Spectrum(customObj):
    '''
    Lines are optionally associated with a spectrum. Most of the
    spectral properties listed here (channel, data type, etc)
    are not actually used, but are included here for ease of
    extensibility to tracking lines across multiple spectra.

    A Spectrum object can hold a full array of frequencies and
    values, which can in turn be accessed to find out (for
    instance) which spectral bin an associated line belongs to.
    '''

    def __init__(self, **kwargs):
        self.validargs = {
            'label': str,  # a label for the spectrum
            "source_file": str,  # path to the source file
            # 'spect' in usual cases; could also be 'list'
            # for linelists with a given resolution
            "source_type": str,
            "freq_array": np.ndarray,
            "val_array": np.ndarray,
            "resolution": float,
            "freq_min": float,
            "freq_max": float,
            "channel": str,
            "epoch_start_gps": int,
            "epoch_duration_sec": int,
            # such as ASD, PSD, coherence, persistence...
            "height_datatype": str,
        }
        customObj.__init__(self, self.validargs, kwargs)
        if self.freq_array is not None:
            if self.resolution:
                raise Exception(
                    "Please do NOT supply both a frequency array and a"
                    " frequency resolution, as these may conflict.")
            if self.freq_min:
                raise Exception(
                    "Please do NOT supply both a frequency array and a"
                    " frequency minimum, as these may conflict.")
            if self.freq_max:
                raise Exception(
                    "Please do NOT supply both a frequency array and a"
                    " frequency maximum, as these may conflict.")
            self.freq_min = self.freq_array[0]
            self.freq_max = self.freq_array[-1]
            self.resolution = (self.freq_max-self.freq_min) / \
                (len(self.freq_array)-1)


def is_equivalent(A, B, tol=None):
    '''
    Accepts two line objects, which may or may not
    be associated with the same spectrum.
    Determines whether they are equivalent.

    Parameters
    ----------
    A: Line object
        First line to compare
    B: Line object
        Second line to compare
    tol: float
        Absolute frequency tolerance, if an explicit value needs
        to be used. Otherwise, will use spectral information.

    Returns
    -------
    bool
        Whether or not the lines are equivalent for
        the given tolerance and/or spectral info.
    '''

    # === Direct comparisons with tolerance

    # if an explicit tolerance was given, use that
    if tol:
        return np.isclose(A.freq, B.freq, atol=tol)

    # === Impossible to compare lines (not enough spectral info)

    # if A and B are unassociated with any spectrum
    # and no tolerance was supplied
    elif (not A.spectrum) or (not B.spectrum):
        raise Exception(
            "These lines cannot be compared. They lack spectrum information"
            " and no tolerance was supplied.")

    # if A and B are associated with spectra, but the resolution is unknown
    elif (not A.spectrum.resolution) or (not B.spectrum.resolution):
        raise Exception(
            "These lines cannot be compared. Their spectra lack resolution"
            " information.")

    # === Spectral info available, ordered best case to worst case

    # if A and B are in the same line list and they both have
    # spectral indices (from any source)
    elif A.spectrum == B.spectrum and A.spectral_index and B.spectral_index:
        return (A.spectral_index == B.spectral_index)

    # if A and B both have spectra with associated frequency arrays
    elif (A.spectrum == B.spectrum) and (A.spectrum.freq_array is not None):
        # Select the lower-resolution spectrum to use for comparison.
        refspect = [A.spectrum, B.spectrum].sort(key=lambda x: x.resolution)[1]
        # compare the indices in the lower-resolution spectrum
        compare_inds = []
        for line in [A, B]:
            if line.spectrum is refspect:
                compare_inds += [line.spectral_index]
            else:
                compare_inds += [match_bins(
                    refspect,
                    [line.freq])[0]]
        return (compare_inds[0] == compare_inds[1])

    # As a last resort, if A and B both have spectra with associated
    # resolution info, work with that info. "Worst" resolution here means
    # largest spectrum.resolution value, widest spacing of bins.
    else:
        worstres = max(A.spectrum.resolution, B.spectrum.resolution)
        return np.isclose(A.freq, B.freq, atol=worstres)
