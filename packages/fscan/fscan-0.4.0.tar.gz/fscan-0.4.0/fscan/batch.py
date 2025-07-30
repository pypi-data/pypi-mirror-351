# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Evan Goetz (2023)
#
# This file is part of fscan

import math
import os
import subprocess


ENVIRONMENT = ['*DATAFIND*', 'KRB5*', 'X509*', 'BEARER_TOKEN*',
               'SCITOKEN*', '*SEGMENT*', 'XDG*']


def write_sub_file(full_path, subname, executable, acctgroup, acctuser,
                   request_disk, request_memory=2000, universe='vanilla',
                   environment=False):

    os.makedirs(os.path.join(full_path, 'logs'), exist_ok=True)

    subcontent = (
        f'universe = {universe}\n'
        f'executable = {executable}\n'
        f'arguments = $(arglist)\n'
        f'accounting_group = {acctgroup}\n'
        f'accounting_group_user = {acctuser}\n'
        f'request_disk = {request_disk}MB\n'
        f'request_memory = {request_memory}MB\n'
        f'log = {full_path}/logs/{subname}.log\n'
        f'error = {full_path}/logs/{subname}.err\n'
        f'output = {full_path}/logs/{subname}.out\n'
        f'notification = never\n')

    if environment:
        subcontent += 'getenv = '
        subcontent += ','.join(ENVIRONMENT)
        subcontent += '\n'

    subcontent += "queue 1\n"

    with open(os.path.join(full_path, f'{subname}.sub'), 'w') as f:
        f.write(subcontent)


def other_sft_ch_idx(chvars, ch_idx):
    """ Find the index for the 'A channel' of the coherence """

    other_ch_idx = -1
    for n in range(len(chvars)):
        if chvars[n]['channel'] == chvars[ch_idx]['coherence']:
            other_ch_idx = n
            break
    assert other_ch_idx >= 0, (
        f"'A channel' {chvars[ch_idx]['coherence']} not found")

    return other_ch_idx


def write_dag(args, epseg_info, channels, chvars):
    """
    This writes out a DAG file that contains the full workflow:
    SFT creation and saving, averaging and normalizing SFTs,
    plotting the data, calculating the coherence and plotting
    """
    dag_filename = os.path.join(epseg_info['epoch_path'], 'SUPERDAG.dag')

    # If a SUPERDAG.dag file already exists, we don't want to append to the
    # file, so check if it does exist, and if so, open a file in write mode
    # so that it effectively erases everything in the file
    if os.path.exists(dag_filename):
        with open(dag_filename, 'w') as f:
            pass

    # If making SFTs from lalpulsar_MakeSFTDAG, use SPLICE to get the DAG file
    # within this DAG
    if args.create_sfts and epseg_info['havesegs']:
        with open(dag_filename, 'a') as f:
            for frametype in channels.keys():
                makesftdagfile = os.path.join(epseg_info['epoch_path'],
                                              f'{frametype}_SFT_GEN',
                                              'makesfts.dag')
                f.write(f"SPLICE {frametype}_SFTs {makesftdagfile}\n")

    if epseg_info['havesegs']:
        with open(dag_filename, 'a') as f:
            for idx, (frametype, chans) in enumerate(channels.items()):
                for (ch_idx, ch) in chans:
                    ch_path = os.path.join(epseg_info['epoch_path'],
                                           ch.replace(':', '_'))

                    subfile = os.path.join(ch_path, 'spectrumAverage.sub')
                    f.write(f'JOB SpecAvg_{ch_idx} {subfile}\n')
                    f.write(f'VARS SpecAvg_{ch_idx} arglist="')
                    f.write(f"--startGPS={epseg_info['SFTGPSstart']}")
                    f.write(f" --endGPS={epseg_info['SFTGPSend']}")
                    f.write(f" --IFO={ch[0:2]}")
                    f.write(f' --fMin={args.fmin}')
                    f.write(f' --fMax={args.fmin + args.band}')
                    f.write(f" --freqRes={chvars[ch_idx]['freq_res']}")
                    f.write(f" --timeBaseline={args.Tsft}")
                    f.write(f' --SFTs={ch_path}/sfts/*.sft')
                    f.write(f' --outputDir={ch_path}')
                    f.write(f' --subband={args.band}')
                    f.write('"\n')

                    if args.create_sfts:
                        f.write(f'PARENT {frametype}_SFTs CHILD '
                                f'SpecAvg_{ch_idx}\n')

                    if args.full_band_avg:
                        subfile = os.path.join(
                            ch_path, 'spectrumAverageLong.sub')
                        f.write(f'JOB SpecAvgLong_{ch_idx} {subfile}\n')
                        f.write(f'VARS SpecAvgLong_{ch_idx} arglist="')
                        f.write(f"--startGPS={epseg_info['SFTGPSstart']}")
                        f.write(f" --endGPS={epseg_info['SFTGPSend']}")
                        f.write(f" --IFO={ch[0:2]}")
                        f.write(f" --fMin={args.fmin}")
                        f.write(f" --fMax={args.fmin + args.band}")
                        f.write(f" --timeBaseline={args.Tsft}")
                        f.write(f" --outputDir={ch_path}")
                        f.write(f" --outputBname=speclong_{args.fmin:.2f}_"
                                f"{(args.fmin+args.band):.2f}_{ch[0:2]}_"
                                f"{epseg_info['SFTGPSstart']}_"
                                f"{epseg_info['SFTGPSend']}")
                        if 'persist_avg_opt' in chvars[ch_idx]:
                            f.write(" --persistAvgOption="
                                    f"{chvars[ch_idx]['persist_avg_opt']}")
                        elif 'persist_avg_sec' in chvars[ch_idx]:
                            f.write(" --persistAvgSeconds="
                                    f"{chvars[ch_idx]['persist_avg_sec']}")
                        if 'auto_track' in chvars[ch_idx]:
                            f.write(" --autoTrack="
                                    f"{chvars[ch_idx]['auto_track']}")
                        f.write(f' --SFTs={ch_path}/sfts/*.sft"\n')
                        if args.create_sfts:
                            f.write(f'PARENT {frametype}_SFTs CHILD '
                                    f'SpecAvgLong_{ch_idx}\n')

                    if 'coherence' in chvars[ch_idx]:
                        subfile = os.path.join(ch_path, 'runCoherence.sub')
                        path_to_other_sfts = os.path.join(
                            epseg_info['epoch_path'],
                            chvars[ch_idx]['coherence'].replace(':', '_'))
                        other_ch_idx = other_sft_ch_idx(chvars, ch_idx)
                        other_sft_frametype = chvars[other_ch_idx]['frametype']
                        f.write(f'JOB Coh_{ch_idx} {subfile}\n')
                        f.write(f'VARS Coh_{ch_idx} arglist="')
                        f.write(f"--startGPS={epseg_info['SFTGPSstart']}")
                        f.write(f" --endGPS={epseg_info['SFTGPSend']}")
                        f.write(f' --fMin={args.fmin}')
                        f.write(f' --fMax={args.fmin + args.band}')
                        f.write(f" --timeBaseline={args.Tsft}")
                        f.write(f' --ChASFTs={path_to_other_sfts}/sfts/*.sft')
                        f.write(f' --ChBSFTs={ch_path}/sfts/*.sft')
                        f.write(f' --outputDir={ch_path}')
                        f.write(f" --outputBname=spec_{args.fmin:.2f}_"
                                f"{(args.fmin+args.band):.2f}_{ch[0:2]}_"
                                f"{epseg_info['SFTGPSstart']}_"
                                f"{epseg_info['SFTGPSend']}_coh")
                        f.write('"\n')

                        if args.create_sfts:
                            f.write(f'PARENT {frametype}_SFTs ')
                            if frametype != other_sft_frametype:
                                f.write(f'{other_sft_frametype}_SFTs ')
                            f.write(f'CHILD Coh_{ch_idx}\n')

    if args.plot_output and epseg_info['havesegs']:
        with open(dag_filename, 'a') as f:
            for idx, (frametype, chans) in enumerate(channels.items()):
                for (ch_idx, ch) in chans:
                    ch_path = os.path.join(epseg_info['epoch_path'],
                                           ch.replace(':', '_'))
                    subfile = os.path.join(ch_path,
                                           'postProcess.sub')

                    # set up list of dag parents for post processing
                    parentstring = f"SpecAvg_{ch_idx}"
                    if args.full_band_avg:
                        parentstring += " "+f"SpecAvgLong_{ch_idx}"
                    if 'coherence' in chvars[ch_idx]:
                        other_ch_idx = other_sft_ch_idx(chvars, ch_idx)
                        parentstring += " "+f"Coh_{ch_idx}"
                        parentstring += " "+f"PostProcess_{other_ch_idx}"

                    f.write(f'JOB PostProcess_{ch_idx} {subfile}\n')
                    f.write(f'VARS PostProcess_{ch_idx} arglist="')
                    f.write(f"--parentPathInput {ch_path}")
                    f.write(" --plot-sub-band "
                            f"{chvars[ch_idx]['plot_sub_band']}")
                    if args.tracked_line_list:
                        f.write(" --tracked-line-list "
                                f"{args.tracked_line_list}")
                    if args.tracked_line_tag:
                        f.write(f" --tracked-line-tag {args.tracked_line_tag}")
                    if args.LF_emailFrom and args.LF_emailTo:
                        f.write(f" --LF-emailFrom {args.LF_emailFrom}")
                        f.write(f" --LF-emailTo {args.LF_emailTo}")
                    if args.delete_ascii:
                        f.write(" --delete-converted-text True")
                    f.write('"\n')
                    f.write(f'PARENT {parentstring} '
                            f'CHILD PostProcess_{ch_idx}\n')

    if args.plot_output:
        with open(dag_filename, 'a') as f:
            subfile = os.path.join(epseg_info['epoch_path'],
                                   'summary.sub')
            f.write(f'JOB Summary {subfile}\n')
            f.write('VARS Summary arglist="')
            f.write(f"--fscan-output-path {args.SFTpath}")
            f.write(f" --chan-opts {args.chan_opts}")
            f.write(f" --Tsft {args.Tsft} ")
            f.write(f" --overlap-fraction {args.overlap_fraction}")
            f.write(f" --intersect-data {args.intersect_data}")
            f.write(" --segment-type")
            for segtype in epseg_info['segtype']:
                f.write(f" {segtype}")
            f.write(f" --analysisStart {epseg_info['epoch_tag']}")
            f.write(f" --analysisDuration {epseg_info['duration_tag']}")
            f.write(f" --averageDuration {args.averageDuration}")
            if args.greedy is not None and args.greedy != '':
                f.write(f" --greedy {args.greedy}")
            f.write('"\n')
            if epseg_info['havesegs']:
                f.write("PARENT")
                for idx, (frametype, chans) in enumerate(channels.items()):
                    for (ch_idx, ch) in chans:
                        f.write(f' PostProcess_{ch_idx}')
                f.write(' CHILD Summary')

    return


class MakeSFTJob(object):

    def __init__(self, args, epseg_info, fr_chans):
        self.args = args
        self.epseg_info = epseg_info
        self.frametype = fr_chans[0]
        self.channels = [ch for (idx, ch) in fr_chans[1]]
        self.channel_sft_paths = [
            os.path.join(self.epseg_info['epoch_path'],
                         ch.replace(':', '_'),
                         'sfts') for ch in self.channels]

    def setup_output(self):
        """
        This makes the directories from the full path:
        SFT path/SFT duration/seg type/epoch type/epoch/channels/sfts
        """
        for p in self.channel_sft_paths:
            os.makedirs(p, exist_ok=True)

        return

    def validate_segments(self):
        """
        This just checks that we have at least one segment with duration Tsft
        """
        assert os.path.exists(self.epseg_info['segfile'])

        seg_list = []
        with open(self.epseg_info['segfile']) as f:
            for idx, seg in enumerate(f):
                seg = seg.split()
                if int(seg[1]) - int(seg[0]) >= self.args.Tsft:
                    seg_list.append([seg[0], seg[1]])

        if len(seg_list) < 1:
            raise ValueError(
                f"No segment found in {self.epseg_info['segfile']}")

        return

    def run_make_sft_dag(self):
        """
        This runs the whole making of SFTs
        """
        self.setup_output()

        try:
            self.validate_segments()
        except ValueError:
            print(f"No segments found for {self.epseg_info['epoch_path']}. "
                  "Skipping this epoch.")
            return 1

        sft_dag_file = os.path.join(self.epseg_info['epoch_path'],
                                    f'{self.frametype}_SFT_GEN',
                                    'makesfts.dag')
        cache_dir = os.path.join(os.path.dirname(sft_dag_file), 'cache')
        logs_dir = os.path.join(os.path.dirname(sft_dag_file), 'logs')

        os.makedirs(os.path.dirname(sft_dag_file), exist_ok=True)

        make_dag_cmd = os.path.join(self.args.make_sft_dag_path,
                                    'lalpulsar_MakeSFTDAG')
        make_dag_cmd += f' -m 1 -G fscan_{self.frametype}'
        make_dag_cmd += f' -O {self.args.observing_run}'
        make_dag_cmd += f' -K {self.args.observing_kind}'
        make_dag_cmd += f' -R {self.args.observing_revision}'
        make_dag_cmd += f' -w {self.args.window_type}'
        make_dag_cmd += f' -P {self.args.overlap_fraction}'
        make_dag_cmd += f' -A {self.args.accounting_group}'
        make_dag_cmd += f' -U {self.args.accounting_group_user}'
        make_dag_cmd += f' -Y {self.args.request_memory}'
        make_dag_cmd += f' -s {self.args.request_disk}'
        make_dag_cmd += f' -d {self.frametype}'
        make_dag_cmd += f' -k {self.args.hp_filter_knee_freq}'
        make_dag_cmd += f' -T {self.args.Tsft}'
        make_dag_cmd += f' -F {self.args.fmin}'
        make_dag_cmd += f' -B {self.args.band}'
        make_dag_cmd += f" -N {' '.join(self.channels)}"
        make_dag_cmd += f" -p {' '.join(self.channel_sft_paths)}"
        make_dag_cmd += f" -C {cache_dir}"
        make_dag_cmd += f" -o {logs_dir}"
        make_dag_cmd += f" -g {self.epseg_info['segfile']}"
        make_dag_cmd += f' -f {sft_dag_file}'
        make_dag_cmd += f' -j {self.args.datafind_path}'
        make_dag_cmd += f' -J {self.args.make_sft_path}'

        if self.args.allow_skipping:
            make_dag_cmd += ' --allow-skipping'
        if self.args.misc_desc:
            make_dag_cmd += ' -X {self.args.misc_desc}'

        subprocess.run(make_dag_cmd.split(), check=True)

        return 0


class ProcessSFTs(object):

    def __init__(self, args, epseg_info, ch):
        self.args = args
        self.epseg_info = epseg_info
        self.ch = ch
        self.full_ch_path = os.path.join(self.epseg_info['epoch_path'],
                                         self.ch['channel'].replace(':', '_'))

        # memory usage calibrated for 1800 s SFTs and 1 week averaging
        self.spec_avg_mem = int(math.ceil(
            128 * (args.Tsft / 1800)
            + 5 * (epseg_info['duration'] / 604800)
            ))
        self.spec_coherence_mem = 2 * self.spec_avg_mem
        self.spec_avg_long_mem = int(math.ceil(
            512 * (args.Tsft / 1800)
            + 1024 * (epseg_info['duration'] / 604800)
            ))
        self.post_process_mem = 8192

    def write_condor_band_sub(self):

        """
        Write the submit file for computing the normalized, averaged spectra
        and the spectrograms using lalpulsar_spec_avg
        """

        write_sub_file(
            full_path=self.full_ch_path,
            subname='spectrumAverage',
            executable=os.path.join(self.args.spec_tools_path,
                                    'lalpulsar_spec_avg'),
            acctgroup=self.args.accounting_group,
            acctuser=self.args.accounting_group_user,
            request_disk=500, request_memory=self.spec_avg_mem)

    def write_condor_full_band_sub(self):

        """
        Write the submit file for computing the normalized, averaged spectra
        using lalpulsar_spec_avg_long
        """

        write_sub_file(
            full_path=self.full_ch_path,
            subname='spectrumAverageLong',
            executable=os.path.join(self.args.spec_tools_path,
                                    'lalpulsar_spec_avg_long'),
            acctgroup=self.args.accounting_group,
            acctuser=self.args.accounting_group_user,
            request_disk=2000, request_memory=self.spec_avg_long_mem)

    def write_condor_coherence_sub(self):
        """
        Write the submit file for computing the coherence from SFTs
        """
        write_sub_file(
            full_path=self.full_ch_path,
            subname='runCoherence',
            executable=os.path.join(self.args.spec_tools_path,
                                    'lalpulsar_spec_coherence'),
            acctgroup=self.args.accounting_group,
            acctuser=self.args.accounting_group_user,
            request_disk=500, request_memory=self.spec_coherence_mem)

    def write_condor_plots_sub(self):
        """
        Write the submit file for computing the plots and follow-on analyses
        using postProcess
        """
        write_sub_file(
            full_path=self.full_ch_path,
            subname='postProcess',
            executable=os.path.join(self.args.postproc_path,
                                    'postProcess'),
            acctgroup=self.args.accounting_group,
            acctuser=self.args.accounting_group_user,
            request_disk=5000,
            request_memory=self.post_process_mem)


class SummaryJob(object):

    def __init__(self, args, epseg_info):
        self.args = args
        self.epoch_path = epseg_info['epoch_path']

    def setup_output(self):
        """
        This makes the directories from the full path:
        SFT path/SFT duration/seg type/epoch type/epoch
        """
        os.makedirs(self.epoch_path, exist_ok=True)

        return

    def write_condor_work_sub(self):
        """
        Write the submit file for producing the Fscan summary page
        """
        self.setup_output()

        write_sub_file(
            full_path=self.epoch_path,
            subname='summary',
            executable=os.path.join(self.args.postproc_path,
                                    'FscanSummaryPage'),
            acctgroup=self.args.accounting_group,
            acctuser=self.args.accounting_group_user,
            request_disk=500,
            universe='local',
            environment=True)
