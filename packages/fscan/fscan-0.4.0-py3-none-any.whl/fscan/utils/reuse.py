# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Ansel Neunzert (2023)
#               Evan Goetz (2023)
#
# This file is part of fscan

import numpy as np
import os
from .dtutils import find_specific_SFT
from .utils import (sft_vals_from_makesft_dag_vars,
                    sft_name_from_vars)


def use_existing_sfts(epseg_info, channels):

    for idx, (frametype, chans) in enumerate(channels.items()):
        sft_dag_file = os.path.join(
            epseg_info['epoch_path'], f'{frametype}_SFT_GEN', "makesfts.dag")

        # If the dag file doesn't exist, then skip
        if not os.path.exists(sft_dag_file):
            continue

        replacejobs = []  # list of job numbers to be replaced
        # open the SFT dag and read the contents
        with open(sft_dag_file, 'r') as sftdag:
            lines = sftdag.readlines()
        # Here we loop over the lines in the DAG file which is equivalent to
        # looping over SFT start times
        for line in lines:
            if "VARS MakeSFTs" in line:
                # Extract the start and end times and Tsft for each SFT from
                # the dag file (note that SFTGPSstart is the start of a
                # *specific* SFT, but epseg_info['SFTGPSstart'] is the start of
                # the *first* SFT in the epoch. Confusing notation, sorry.)
                pars = sft_vals_from_makesft_dag_vars(line)

                # Loop over the channels and mark whether the SFT was found or
                # not with the found filepath
                found_sft_files = np.zeros(len(pars[6]), dtype='<U256')
                found_sfts = 0
                for idx, ch_tup in enumerate(chans):
                    # create filename
                    sftname = sft_name_from_vars(
                        pars[0], pars[1], pars[2], pars[3], pars[4], pars[5],
                        ch_tup[1])
                    # find the matching SFT path if one exists
                    # this may return "<path>/nosfts" if the channel is not in
                    # frames or has too-low sampling frequency
                    foundSFTpath = find_specific_SFT(
                        sftname, epseg_info['segtype_path'], ch_tup[1],
                        exclude=[epseg_info['duration_tag']],
                        mode=None)  # we might want to change the mode later
                    if foundSFTpath != '':
                        assert len(foundSFTpath) <= 256, (
                            f"{foundSFTpath} is longer than 256 characters")
                        found_sft_files[idx] = foundSFTpath
                        found_sfts += 1

                # If all the SFTs were found, then we can comment out this SFT
                # job
                # TODO: could modify the SFT job so that only need to generate
                #       the SFTs that were not found by modifying the VARS for
                #       this job in makesfts.dag
                if found_sfts == len(found_sft_files):
                    for idx, ch_tup in enumerate(chans):
                        # create the destination path (where we should make the
                        # symlink)
                        newSFTpath = os.path.join(
                            pars[7][idx],
                            os.path.basename(found_sft_files[idx]))
                        # link the old SFT (if it hasn't already been linked)
                        # and the old SFT is not already a symlink
                        if (not os.path.exists(newSFTpath) and
                                not os.path.islink(found_sft_files[idx])):
                            os.symlink(found_sft_files[idx], newSFTpath)
                    # record the job number of the line; we will comment it out
                    jobnum = line.split(" MakeSFTs_")[1].split(" ")[0]
                    replacejobs += [jobnum]

        # we are going to overwrite the SFT dag content; initialize it
        newsftdag_content = ""
        # this variable will track whether there are any SFT jobs that will
        # need to remain in the dag (SFTs that don't already exist elsewhere)
        remaining_sftjobs = False
        # Iterate through the SFT dag again, commenting out all parts of
        # the jobs we don't need (data finding and SFT creation).
        for line in lines:
            writeline = True
            for r in replacejobs:
                if (f" datafind_{r} " in line) or (f" MakeSFTs_{r} " in line):
                    writeline = False
            if writeline:
                newsftdag_content += line
                remaining_sftjobs = True
            else:
                newsftdag_content += f"# {line}"

        # Write the new content
        with open(sft_dag_file, 'w') as sftdag:
            sftdag.write(newsftdag_content)

        # If nothing remains uncommented in the SFT dag file, we will need to
        # comment out the "spliceSFTDAG" lines from the SUPERDAG.
        # Note that this does not only appear on the first line, but also in a
        # parent/child relationship later.
        if not remaining_sftjobs:
            print("All SFTS were found in other directories")
            superdagfile = os.path.join(
                epseg_info['epoch_path'], "SUPERDAG.dag")
            newsuperdag_content = ""
            with open(superdagfile, 'r') as superdag:
                superlines = superdag.readlines()
            for line in superlines:
                if f"{frametype}_SFTs" not in line:
                    newsuperdag_content += line
                else:
                    newsuperdag_content += f"# {line}"
            with open(superdagfile, 'w') as superdag:
                superdag.write(newsuperdag_content)

    return
