import json
import os
import subprocess
import tempfile
from itertools import product
from pathlib import Path

import pandas as pd
import pytest

from blabpy.seedlings.io import read_all_basic_level
from blabpy.seedlings.pipeline import make_updated_all_basic_level_here, get_amended_audio_regions, \
    get_processed_audio_regions, get_top3_top4_surplus_regions, gather_recording_seedlings_nouns, \
    _gather_corpus_seedlings_nouns
from blabpy.utils import pandas_df_hash


def test_make_updated_all_basic_level_here(tmpdir):
    """
    Only checks that all_basiclevel can be successfully created. Require connection to BLab share.
    """
    with tmpdir.as_cwd():
        make_updated_all_basic_level_here()
        cwd = Path()
        for ending, extension in product(('', '_NA'), ('.csv', '.feather')):
            filename = 'all_basiclevel' + ending + extension
            assert cwd.joinpath(filename).exists()


@pytest.mark.parametrize('subject, month', [(20, 12), (6, 7), (22, 7)])
def test_get_amended_audio_regions(subject, month):
    get_amended_audio_regions(subject, month)


def test_get_processed_audio_regions():
    try:
        get_processed_audio_regions(8, 12)
    except Exception as e:
        pytest.fail(f"Failed to get processed audio regions for 08_12: {e}")

    special_case_regions_auto = get_processed_audio_regions(20, 12, amend_if_special_case=False)
    special_case_regions_amended = get_processed_audio_regions(20, 12, amend_if_special_case=True)
    assert not special_case_regions_auto.equals(special_case_regions_amended)


@pytest.mark.parametrize('subject, month', [(6, 7), (8, 9), (10, 14)])
def test_get_top3_top4_surplus_regions(subject, month):
    get_top3_top4_surplus_regions(subject, month)


@pytest.fixture(scope='module')
def seedlings_nouns_data_dir():
    return Path(__file__).parent / 'data' / 'seedlings_nouns'


def load_test_data(top3_top4_surplus_data_dir, filename, dtype=None, parse_dates=False):
    return pd.read_csv(top3_top4_surplus_data_dir / filename, dtype=dtype, parse_dates=parse_dates).convert_dtypes()


def test_gather_everything_for_seedlings_nouns(top3_top4_surplus_data_dir, seedlings_nouns_data_dir):
    recording_basic_level = pd.read_csv(top3_top4_surplus_data_dir / 'input_tokens.csv').convert_dtypes()

    (actual_regions_for_seedlings_nouns,
     actual_tokens_full,
     actual_recordings,
     actual_total_listened_time_ms,
     actual_total_recorded_time_ms) = gather_recording_seedlings_nouns('Audio', 2, 8, recording_basic_level)

    expected_regions_for_seedlings_nouns = load_test_data(seedlings_nouns_data_dir, 'regions_for_seedlings_nouns.csv')
    expected_tokens_full = load_test_data(seedlings_nouns_data_dir, 'tokens_full.csv')
    expected_recordings = load_test_data(seedlings_nouns_data_dir, 'recordings.csv', parse_dates=['start', 'end'])
    total_times = json.load(open(seedlings_nouns_data_dir / 'total_times.json'))
    expected_total_listened_time_ms = total_times['total_listened_time_ms']
    expected_total_recorded_time_ms = total_times['total_recorded_time_ms']

    assert actual_regions_for_seedlings_nouns.equals(expected_regions_for_seedlings_nouns)
    assert actual_tokens_full.equals(expected_tokens_full)
    assert actual_recordings.equals(expected_recordings)
    assert actual_total_listened_time_ms == expected_total_listened_time_ms
    assert actual_total_recorded_time_ms == expected_total_recorded_time_ms


@pytest.fixture(scope='module')
def dummy_all_basic_level():
    """Used exclusively for testing gather_recording_seedlings_nouns on specific recordings. Don't use for testing
    anything else."""
    rows = [
        ('Audio_01_08', 1, 6300000, 6300000 + 1, '', 'd', 'y', '', '', '', '01', '08', '01_08', '', '', ''),
        ('Audio_12_16', 1, 7500000, 7500000 + 1, '', 'd', 'n', '', '', '', '12', '16', '12_16', '', '', ''),
        ('Audio_12_17', 1, 1800000, 1800000 + 1, '', 'n', 'y', '', '', '', '12', '17', '12_17', '', '', ''),
        ('Audio_26_13', 1, 300000, 300000 + 1, '', 'd', 'y', '', '', '', '26', '13', '26_13', '', '', '')]
    columns = ['recording_id', 'ordinal', 'onset', 'offset', 'object', 'utterance_type',
               'object_present', 'speaker', 'basic_level', 'annotid', 'child', 'month',
               'subject_month', 'audio_video', 'transcription', 'global_basic_level']
    return pd.DataFrame(data=rows, columns=columns)


@pytest.mark.parametrize('recording_id', ('Audio_26_13', 'Audio_01_08', 'Audio_12_17', 'Audio_12_16'))
def test_gather_recording_seedlings_nouns(recording_id, dummy_all_basic_level):
    """
    Checking that the function works on recordings that don't have an its file (26_13, 01_08), on recordings that don't
    have timezone info in their its file (12_17), and on recordings that have both (12_16).
    """
    recording_basic_level = dummy_all_basic_level.loc[lambda df: df.recording_id == recording_id]
    gather_recording_seedlings_nouns(recording_id, recording_basic_level)


@pytest.fixture(scope='module')
def all_basic_level_df():
    # Use blabr to create all_basic_level.csv and write it to tmp_path
    with tempfile.TemporaryDirectory() as temp_dir:
        all_basic_level_path = os.path.join(temp_dir, 'all_basic_level.csv')
        r_code = f"""
            all_bl <- blabr::get_all_basiclevel(version = '0.6.0');
            readr::write_csv(all_bl, '{all_basic_level_path}', quote = 'all')
            """
        r_code = ''.join(r_code.split('\n'))
        subprocess.run(['Rscript', '-e', r_code], cwd=temp_dir, check=True)

        # Read all_basic_level.csv
        return read_all_basic_level(all_basic_level_path)


def test__gather_corpus_seedlings_nouns(all_basic_level_df):
    """
    Tests the output of _gather_corpus_seedlings_nouns on a small subset of the data.
    Requires blabr to be installed and `all_basiclevel` and `global_basic_level` to have been cloned to ~/BLAB_DATA.
    :return:
    """
    all_basic_level_df = all_basic_level_df.loc[lambda df: df.month.isin(['06', '10', '14', '17'])
                                                                 & df.subj.isin(['01', '25', '46'])]
    seedlings_nouns, regions, sub_recordings, recordings = _gather_corpus_seedlings_nouns(all_basic_level_df)

    assert pandas_df_hash(seedlings_nouns) == '9af98d01ff1714e328196c0acaa1a725647323b0797dc1b1361f7f3a61fe9e03'
    assert pandas_df_hash(regions) == 'f911dc162ceeda249b67ca3c8a3c7352d5c5894b4b87e8699b0d54077a070c5a'
    assert pandas_df_hash(sub_recordings) == 'd766b009961bb6e33dd0e2d513b65721c00aa796304e7ed788251040dd6ed47f'
    assert pandas_df_hash(recordings) == '5e09f31c4c7cf3f7b29147442dd36690930f7aaf857ee8e9a46568b13e1ebf80'
