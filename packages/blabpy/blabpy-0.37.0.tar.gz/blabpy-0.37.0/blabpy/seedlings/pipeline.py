import os
import subprocess
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pkg_resources
from tqdm import tqdm

from .regions.top3_top4_surplus import TOP_4_KIND, TOP_3_KIND
from ..blab_data import get_file_path, switch_dataset_to_version
from . import AUDIO, VIDEO, MISSING_TIMEZONE_FORCED_TIMEZONE, MISSING_TIMEZONE_RECORDING_IDS, \
    SUB_RECORDINGS_SPECIAL_CASES
from .cha import export_cha_to_csv
from .codebooks import make_codebook_template
from .gather import gather_all_basic_level_annotations, check_for_errors
from .io import blab_write_csv, SEEDLINGS_NOUNS_DTYPES, SEEDLINGS_NOUNS_SORT_BY, \
    SEEDLINGS_NOUNS_SUB_RECORDINGS_DTYPES, SEEDLINGS_NOUNS_RECORDINGS_DTYPES, \
    read_video_recordings_csv, read_seedlings_codebook, write_all_basic_level_to_csv, \
    SEEDLINGS_NOUNS_REGIONS_LONG_DTYPES, SEEDLINGS_NOUNS_REGIONS_WIDE_DTYPES, read_all_basic_level
from .listened_time import listen_time_stats_for_report, _get_subregion_count, _preprocess_region_info, RegionType
from .merge import create_merged, FIXME
from .opf import export_opf_to_csv
from .paths import get_all_opf_paths, get_all_cha_paths, get_basic_level_path, _parse_out_child_and_month, \
    _check_modality, get_seedlings_path, get_cha_path, get_opf_path, _normalize_child_month, get_lena_5min_csv_path, \
    get_its_path, split_recording_id
from .regions import get_processed_audio_regions as _get_processed_audio_regions, _get_amended_regions, \
    SPECIAL_CASES as REGIONS_SPECIAL_CASES, get_top3_top4_surplus_regions as _get_top3_top4_surplus_regions, \
    assign_tokens_to_regions, reformat_seedlings_nouns_regions
# Placeholder value for words without the basic level information
from .regions.regions import calculate_listened_time, calculate_recording_duration, \
    calculate_total_surplus_time_ms
from .scatter import copy_all_basic_level_files_to_subject_files
from .. import ANONYMIZATION_DATE
from ..its import Its, ItsNoTimeZoneInfo
from ..utils import ensure_folder_exists_and_empty


def export_all_opfs_to_csv(output_folder: Path, suffix='_processed'):
    """
    Exports all opf files, adds suffix to their names and saves to the output_folder
    :param output_folder: Path p
    :param suffix: str
    :return:
    """
    ensure_folder_exists_and_empty(output_folder)

    opf_paths = get_all_opf_paths()
    seedlings_path = get_seedlings_path()
    for opf_path in tqdm(opf_paths, desc='Exporting opf files'):
        # Add suffix before all extensions
        extensions = ''.join(opf_path.suffixes)
        output_name = opf_path.name.replace(extensions, suffix + '.csv')

        export_opf_to_csv(opf_path=opf_path, csv_path=(output_folder / output_name))


def export_all_chas_to_csv(output_folder: Path, log_path=Path('cha_parsing_errors_log.txt')):
    """
    Exports all cha files to output_folder
    :param output_folder: Path
    :param log_path: Path, file where errors are logged if any
    :return: Path|None, if there were any errors, returns path to the error log file
    """
    ensure_folder_exists_and_empty(output_folder)

    # These will hold paths to files with problems if any
    could_not_be_parsed = list()
    parsed_with_errors = list()

    cha_paths = get_all_cha_paths()
    seedlings_path = get_seedlings_path()
    for cha_path in tqdm(cha_paths, desc='Exporting cha files'):
        problems = export_cha_to_csv(cha_path=cha_path, output_folder=output_folder)
        if not problems:
            continue

        # If there were any problems, take note
        if problems == cha_path:
            could_not_be_parsed.append(problems)
        else:
            parsed_with_errors.append((cha_path, problems))

    # Write errors to the log file
    if could_not_be_parsed or parsed_with_errors:
        with log_path.open('w', encoding='utf-8') as f:

            if could_not_be_parsed:
                f.write('The following files could not be parsed:\n\n')
                for path in could_not_be_parsed:
                    f.write(str(path) + '\n')

            if parsed_with_errors:
                f.write('The following files were parsed with errors:\n\n')
                for cha_path, error_path in parsed_with_errors:
                    f.write(f'Cha file: {str(cha_path.absolute())}\n')
                    f.write(f'Error log: {str(error_path.absolute())}\n')
    else:
        log_path = None

    if parsed_with_errors:
        warnings.warn(f'Some cha files were parsed with errors. For details, see:\n {str(log_path.absolute())}')

    if could_not_be_parsed:
        raise Exception(f'Some cha files could not parsed at all. Try exportint them individually. For details, see:\n'
                        f' {str(log_path.absolute())}')

    return log_path


def merge_annotations_with_basic_level(exported_annotations_folder, output_folder, mode,
                                       exported_suffix='_processed.csv'):
    """
    Merges all exported annotation files in output_folder and saves them to output_folder which must be empty.
    :param exported_annotations_folder: the input folder
    :param output_folder: the output folder
    :param mode: 'audio'|'video' - which modality these files came from
    :param exported_suffix: the ending of the exported annotation file names, needed because export_cha_to_csv exports
    two files: the actual csv and the errors file
    :return: 
    """
    ensure_folder_exists_and_empty(output_folder)

    # Find/assemble all necessary paths
    annotation_files = list(exported_annotations_folder.glob(f'*{exported_suffix}'))
    basic_level_files = [get_basic_level_path(**_parse_out_child_and_month(annotation_file), modality=mode.capitalize())
                         for annotation_file in annotation_files]
    output_files = [output_folder / basic_level_file.name for basic_level_file in basic_level_files]

    # Merge and save
    seedlings_path = get_seedlings_path()

    results = [create_merged(file_new=annotation_file, file_old=basic_level_file, file_merged=output_file, mode=mode)
               for annotation_file, basic_level_file, output_file
               in tqdm(zip(annotation_files, basic_level_files, output_files),
                       desc=f'Merging {mode} files')]

    # Output merging log to a csv file
    columns = ['duplicates_in_old_file', 'words_were_edited', 'words_were_added']
    results_df = pd.DataFrame(columns=columns,
                              data=results)
    results_df['exported_annotations_path'] = [annotation_file.absolute() for annotation_file in annotation_files]
    log = Path(f'merging_{mode}_log.csv')
    results_df.to_csv(path_or_buf=log, index=False)

    # Print numbers of files with duplicates, edited words and edited words
    duplicate_count, edited_count, added_count = results_df[columns].sum()
    print(f'There were:\n'
          f'{duplicate_count} basic level files with duplicate annotation ids.\n',
          f'{edited_count} merged files with words that have been edited.\n'
          f'{added_count} merged files with new words.\n\n'
          f'For details, see {log.absolute()}')


def _with_basic_level_folder(working_folder: Path, modality):
    """
    Returns the name of the folder to output annotations merged with previous basic level data.
    This function exists to avoid hard-coding the folder name in the functions that refer to it.
    :param working_folder: the parent folder
    :param modality: Audio/Video
    :return:
    """
    _check_modality(modality)
    return working_folder / f'with_basic_level_{modality.lower()}_annotations'


def merge_all_annotations_with_basic_level(
        exported_audio_annotations_folder, exported_video_annotations_folder,
        working_folder, exported_suffix='_processed.csv'):
    """
    Runs merge_annotations_with_basic_level on both audio and video annotations and puts the results to csv files in
    subfolders of working_folder.
    :param exported_audio_annotations_folder: folder to look for exported audio annotations in
    :param exported_video_annotations_folder: folder to look for exported video annotations in
    :param working_folder: the parent folder of the two output folders.
    :param exported_suffix: see merge_annotations_with_basic_level docstring
    :return:
    """
    # Audio
    with_basic_level_audio_folder = _with_basic_level_folder(working_folder, AUDIO)
    merge_annotations_with_basic_level(exported_annotations_folder=exported_audio_annotations_folder,
                                       output_folder=with_basic_level_audio_folder,
                                       mode='audio', exported_suffix=exported_suffix)

    # Video
    with_basic_level_video_folder = _with_basic_level_folder(working_folder, VIDEO)
    merge_annotations_with_basic_level(exported_annotations_folder=exported_video_annotations_folder,
                                       output_folder=with_basic_level_video_folder,
                                       mode='video', exported_suffix=exported_suffix)

    return with_basic_level_audio_folder, with_basic_level_video_folder


def make_incomplete_basic_level_list(merged_folder: Path):
    """
    Looks through all the files in the folder with annotations merged with previous basic level data and counts the
    number of rows that have to be manually updated
    :param merged_folder:
    :return: a pandas dataframe with two columns: filename, fixme_count
    """
    all_fixmes_df = None
    for csv_file in merged_folder.glob('*.csv'):
        fixmes_df = pd.read_csv(csv_file)
        fixmes_df = fixmes_df[fixmes_df.basic_level == FIXME]
        fixmes_df['filename'] = str(csv_file)
        all_fixmes_df = pd.concat([all_fixmes_df, fixmes_df])
    return all_fixmes_df


def is_any_missing_basic_level_data(merged_folder: Path, list_path: Path):
    """
    Runs make_incomplete_basic_level_list, saves it to a file and return whether there were any missing basic levels.
    :param merged_folder:
    :param list_path: where to output a list of rows missing basic level data
    :return: whether there were any rows with missing basic level data
    """
    df = make_incomplete_basic_level_list(merged_folder=merged_folder)
    df.to_csv(list_path, index=False)
    return df.size > 0


def check_all_basic_level_for_missing(merged_folder_audio, merged_folder_video, working_folder,
                                      raise_error_if_any_missing=True):
    """
    Runs is_any_missing_basic_level_data on both the audio and video folder with annotations merged with existing basic
    level data.
    :param merged_folder_audio:
    :param merged_folder_video:
    :param working_folder: the folder where list of missing basic level data will be saved if any
    :param raise_error_if_any_missing: should an error be raise if there are any missing?
    :return: were there any rows with missing basic levels?
    """
    missing_audio_basic_level_path = working_folder / 'missing_basic_level_audio.csv'
    is_missing_audio = is_any_missing_basic_level_data(merged_folder=merged_folder_audio,
                                                       list_path=missing_audio_basic_level_path)

    missing_video_basic_level_path = working_folder / 'missing_basic_level_video.csv'
    is_missing_video = is_any_missing_basic_level_data(merged_folder=merged_folder_video,
                                                       list_path=missing_video_basic_level_path)

    anything_missing = is_missing_audio or is_missing_video
    if anything_missing:
        if raise_error_if_any_missing:
            raise Exception('Some rows have missing basic level data. For details, see:\n'
                            f'{missing_audio_basic_level_path}\n'
                            f'{missing_video_basic_level_path}\n')
        else:
            return True
    else:
        return False


def export_all_annotations_to_csv(working_folder=None, ignore_audio_annotation_problems=False):
    """
    Exports audio and video annotations to csv files in subfolders of working_folder.
    :param working_folder: the parent folder of the output folders
    :param ignore_audio_annotation_problems: if False, will raise an exception if there were some problems when
    exporting audio annotations
    :return: tuple of paths to exported audio and video annotations respectively
    """
    working_folder = working_folder or Path('')

    # Video annotations
    exported_video_annotations_folder = working_folder / 'exported_video_annotations'
    export_all_opfs_to_csv(exported_video_annotations_folder)

    # Audio annotations
    exported_audio_annotations_folder = working_folder / 'exported_audio_annotations'
    log = export_all_chas_to_csv(exported_audio_annotations_folder)
    if log and not ignore_audio_annotation_problems:
        raise Exception('There were problems during the export of audio annotations.'
                        ' See the following file for details:\n'
                        f'{log.absolute()}')

    return exported_audio_annotations_folder, exported_video_annotations_folder


def make_updated_basic_level_files(working_folder=None, ignore_audio_annotation_problems=False):
    """
    Creates updated versions of individual basic level files:
     - exports all annotations from cha and opf files, checks for exporting errors,
     - uses annotids to find basic level data in the current basic level files, mark rows where new one should be added.
    """
    working_folder = working_folder or Path('')
    ensure_folder_exists_and_empty(working_folder)

    # Export
    exported_audio, exported_video = export_all_annotations_to_csv(
        working_folder=working_folder,
        ignore_audio_annotation_problems=ignore_audio_annotation_problems)

    # Merge with current basic level data
    merge_all_annotations_with_basic_level(
        exported_audio_annotations_folder=exported_audio,
        exported_video_annotations_folder=exported_video,
        working_folder=working_folder
    )

    print('\nThe annotations have been exported and merged with existing basic level data.\n'
          'Use scatter_updated_basic_level_files to check for basic levels that need updating amd move them to \n'
          'SubjectFiles.')


def scatter_updated_basic_level_files(working_folder=None, skip_backups_if_exist=False):
    """
    Checks for missing basic level data in updated sparse_code csv files.
    If there are none, copies the files to their place on BLab share, making a backup there first.
    :return:
    """
    working_folder = working_folder or Path('')
    merged_folders = {modality: _with_basic_level_folder(working_folder, modality) for modality in (AUDIO, VIDEO)}

    anything_missing = check_all_basic_level_for_missing(
        merged_folder_audio=merged_folders[AUDIO],
        merged_folder_video=merged_folders[VIDEO],
        working_folder=working_folder,
        raise_error_if_any_missing=False)

    if anything_missing:
        print('\n'.join([
            'There were rows with missing basic level data. Check the "missing_basic_level_*.csv" files for a list of '
            'the rows.',
            '',
            '- Update the corresponding rows in the individual sparse_code csvs in the following folders:',
            f'  {merged_folders[AUDIO]}',
            f'  {merged_folders[VIDEO]}',
            '\n',
            '- Run scatter_updated_basic_level_files again.'
        ]))
        return

    for modality in (AUDIO, VIDEO):
        copy_all_basic_level_files_to_subject_files(
            updated_basic_level_folder=merged_folders[modality], modality=modality, backup=False,
            skip_backups_if_exist=skip_backups_if_exist)


def make_updated_all_basic_level_here():
    """
    Gathers all basic level files, checks for errors, and writes the result to "all_basiclevel_NA.csv".

    The file is deleted at the very beginning to distinguish two outcomes:
    - everything went well, but there are no changes (files are the same, git status sees no changes) and
    - something went wrong (files are missing, git status will show that much).
    :return: None
    """
    # Delete current version. It is ok if you've already deleted it manually.
    output_path = Path('all_basiclevel_NA.csv')
    try:
        output_path.unlink()
    except FileNotFoundError:
        pass

    # Gather all individual basic level files
    all_basic_level_with_na = gather_all_basic_level_annotations(keep_basic_level_na=True)

    # Check for errors
    errors_df = check_for_errors(all_basic_level_with_na)
    if errors_df is not None:
        errors_file = 'errors.csv'
        errors_df.to_csv(errors_file, index=False)
        raise Exception(f'The were errors found, the corresponding rows are in "{errors_file}".')

    # Save to file
    write_all_basic_level_to_csv(all_basic_level_df=all_basic_level_with_na,
                                 csv_path=output_path)

    assert output_path.exists()
    print(f'all_basiclevel_NA.csv has been created and checked for errors.')


def calculate_listen_time_stats_for_cha_file(cha_path):
    """
    Runs listened_time.listen_time_stats_for_report on a single file accounting for files with four subregions.
    :param cha_path: path to the clan file
    :return: see listened_time.listen_time_stats_for_report
    """
    subregion_count = _get_subregion_count(**_parse_out_child_and_month(cha_path))
    clan_file_text = Path(cha_path).read_text()
    return listen_time_stats_for_report(clan_file_text=clan_file_text, subregion_count=subregion_count)


def preprocess_region_info(cha_path):
    """
    Extract enough info about the regions from a chat file to calculate listen time stats.
    This function does a half of what calculate_listen_time_stats_for_cha_file does.
    :param cha_path: path to the clan file
    :return: see `_preprocess_region_info`
    """
    subregion_count = _get_subregion_count(**_parse_out_child_and_month(cha_path))
    clan_file_text = Path(cha_path).read_text()
    return _preprocess_region_info(clan_file_text=clan_file_text, subregion_count=subregion_count)


def calculate_listen_time_stats_for_all_cha_files():
    """
    Runs calculate_listen_time_stats_for_cha_file on all cha files.
    :return: a pandas DataFrame with the calculated states and an additional column 'filename'
    """
    cha_paths = get_all_cha_paths()
    stats = [calculate_listen_time_stats_for_cha_file(cha_path) for cha_path in cha_paths]

    # Check uniqueness of the keys in all returned dicts
    [keys] = {tuple(stats_.keys()) for stats_ in stats}
    # Check that the keys are what we expect them to be
    expected_keys = ('num_makeup_region',
                     'num_extra_region',
                     'num_surplus_region',
                     'makeup_time',
                     'extra_time',
                     'surplus_time',
                     'subregion_time',
                     'num_subregion_with_annot',
                     'skip_silence_overlap_hour',
                     'skip_time',
                     'silence_time',
                     'silence_raw_hour',
                     'end_time',
                     'total_listen_time',
                     'positions',
                     'ranks',
                     'subregion_raw_hour',
                     'num_raw_subregion',
                     'annotation_counts_raw')
    assert keys == expected_keys

    # Combine into a dataframe and return
    return pd.DataFrame(
        index=pd.Index(data=[cha_path.name for cha_path in cha_paths], name='filename'),
        data=stats,
        columns=expected_keys).reset_index()


def export_and_add_basic_level(subject, month, modality):
    """
    Extracts the relevant information from the cha file and merges it with the basic level annotations. Creates two
    files in the current working directory:
    - <subj>_<month>_sparse_code_processed.csv - the exported file,
    - <subj>_<month>_audio_sparse_code.csv - the merged file.
    :param subject: int/str, subject id
    :param month: int/str, month
    :param modality: str, modality, one of 'Audio', 'Video'
    :return: path to the merged file
    """
    _check_modality(modality)
    subject, month = _normalize_child_month(subject, month)

    # export to csv
    exported_file_path = f'{subject}_{month}_sparse_code_processed.csv'
    if modality == AUDIO:
        mode = 'audio'
        cha_path = get_cha_path(subject, month)
        export_cha_to_csv(cha_path, '.')
    elif modality == VIDEO:
        mode = 'video'
        opf_path = get_opf_path(subject, month)
        export_opf_to_csv(opf_path, Path(exported_file_path))

    # merge with the current sparse_code_csv
    file_new = f'{subject}_{month}_sparse_code_processed.csv'
    file_old = get_basic_level_path(subject, month, modality)
    file_merged = f'{file_old.name}'
    create_merged(file_new=file_new, file_old=file_old, file_merged=file_merged, mode=mode)

    return file_merged


def export_and_add_basic_level_audio(subject, month):
    return export_and_add_basic_level(subject, month, AUDIO)


def export_and_add_basic_level_video(subject, month):
    return export_and_add_basic_level(subject, month, VIDEO)


def _load_lena5min_csv(lena5min_path):
    return (
        pd.read_csv(lena5min_path, index_col=False, usecols=['CTC.Actual', 'CVC.Actual'])
            .rename(columns={'CTC.Actual': 'ctc', 'CVC.Actual': 'cvc'}))


def get_amended_audio_regions(subject, month):
    """
    For the three audio recordings for which processed regions had to be manually amended, returns the amended version.
    :param subject: str/int, subject
    :param month: str/int, month
    :return: a pandas dataframe with the amended processed regions
    """
    subject, month = _normalize_child_month(subject, month)
    subj_month = f'{subject}_{month}'
    assert subj_month in REGIONS_SPECIAL_CASES, f'Not a special case: {subj_month}'

    processed_regions_auto = get_processed_audio_regions(subject, month, amend_if_special_case=False)
    return _get_amended_regions(subj_month, processed_regions_auto)


# TODO: get_amended_audio_regions and this function both call each other. It works, but it's fragile.
#  Separate get_processed_audio_regions(subject, month, amend_if_special_case=False) into two functions:
#  - _get_processed_audio_regions(subject, month)  # amend_if_special_case=False
#  - get_processed_audio_regions(subject, month, amend_if_special_case)  # don't supply default value
def get_processed_audio_regions(subject, month, amend_if_special_case=False):
    """
    Extract regions from the cha file and processes them - removes overlaps in favor of the more important region of the
    two. See blabpy.seedlings.regions.get_processed_audio_regions for details.
    :param subject: int/str, subject id
    :param month: int/str, month
    :param amend_if_special_case: bool, whether to use manually amended regions for the three special cases, see
    :return: see blabpy.seedlings.regions.get_processed_audio_regions
    """
    subject, month = _normalize_child_month(subject, month)
    cha_path = get_cha_path(subject, month)

    if amend_if_special_case is True and f'{subject}_{month}' in REGIONS_SPECIAL_CASES:
        return get_amended_audio_regions(subject, month)

    if month in ('06', '07'):
        lena5min_df = _load_lena5min_csv(get_lena_5min_csv_path(subject, month))
    else:
        lena5min_df = None

    return _get_processed_audio_regions(cha_path=cha_path, lena5min_df=lena5min_df)


def get_top3_top4_surplus_regions(subject, month):
    """
    For the audio recordings, assigns each processed region as either belonging to top3, top4, or surplus.
    :param subject: int/str, subject id
    :param month: int/str, month
    :return: a pandas dataframe with processed regions and their top3/top4/surplus status
    """
    subject, month = _normalize_child_month(subject, month)
    processed_regions = get_processed_audio_regions(subject, month, amend_if_special_case=True)
    return _get_top3_top4_surplus_regions(processed_regions, month)


def _load_sub_recordings_for_special_cases(recording_id):
    """
    Loads data for special cases:
    - Audio_45_10 had extra 10 hours at the beginning of the .its,
    - Audio_06_17 was cropped at the end in the wav file but not .its/.cha.
    """
    assert recording_id.lower() in SUB_RECORDINGS_SPECIAL_CASES, f'Not a special case: {recording_id}'
    special_cases_dir = f'sub-recordings_special-cases/{recording_id}'
    recordings_processed_original_path = os.path.join(special_cases_dir, 'sub-recordings_original.csv')
    recordings_processed_amended_path = os.path.join(special_cases_dir, 'sub-recordings_amended.csv')

    def load_csv(relative_path):
        dtypes = {'recording_id': pd.StringDtype(),
                  'start_ms': pd.Int32Dtype(),
                  'end_ms': pd.Int32Dtype()}
        stream = pkg_resources.resource_stream(__name__, relative_path)

        df = pd.read_csv(stream, dtype=dtypes, encoding='utf-8', parse_dates=['start_dt', 'end_dt'])

        assert df.recording_id.eq(recording_id).all()
        return df.drop(columns='recording_id')

    recordings_processed_original = load_csv(recordings_processed_original_path)
    recordings_processed_amended = load_csv(recordings_processed_amended_path)

    return recordings_processed_original, recordings_processed_amended


def get_lena_sub_recordings(recording_id, amend_if_special_case=False):
    """
    Get anonymized information about sub-recordings of the LENA recording for the given subject and month. There are
    several special cases of sub-recordings that are missing an its file or that have one but it doesn't contain the
    timezone information. See __init__.py for details.

    If there are pauses in LENA sub-recordings, LENA still outputs one big wav file. This leads to confusion and errors,
    such as when an interval spans multiple sub-recordings. It is important to know about these pauses.

    :param recording_id: full recording id, e.g. 'Video_01_16'
    :param amend_if_special_case: whether to use manually amended sub-recordings for the special case of Audio_45_10
    :return: a pandas dataframe with the LENA sub-recordings and the total duration of all sub-recordings
    """
    # TODO: figure out why the timezone info is missing
    if recording_id in MISSING_TIMEZONE_RECORDING_IDS:
        forced_timezone = MISSING_TIMEZONE_FORCED_TIMEZONE
    else:
        forced_timezone = None
    subject, month = recording_id.split('_')[1:3]
    its = Its.from_path(get_its_path(subject, month), forced_timezone=forced_timezone)

    try:
        sub_recordings = its.gather_sub_recordings(anonymize=True)
    except ItsNoTimeZoneInfo as e:
        raise ItsNoTimeZoneInfo(f'No timezone info for {subject}_{month}. Please force a timezone using'
                                f'`forced_timezone`') from e

    # Replace sub-recordings for one special case - Audio_45_10 where .its was longer than .wav and .cha
    if amend_if_special_case and recording_id.lower() in SUB_RECORDINGS_SPECIAL_CASES:
        sub_recordings_original, sub_recordings_amended = _load_sub_recordings_for_special_cases(recording_id)
        # converting to str first to ignore column data types
        assert sub_recordings.astype('str').equals(sub_recordings_original.astype('str'))
        sub_recordings = sub_recordings_amended

    duration_ms = calculate_recording_duration(sub_recordings=sub_recordings)
    return sub_recordings, duration_ms


def _sort_tokens(tokens_df):
    """
    Sorts all_basiclevel/seedlings_nouns
    :param tokens_df: a dataframe to sort
    :return: sorted dataframe
    """
    sort_by = SEEDLINGS_NOUNS_SORT_BY['seedlings-nouns.csv'].copy()
    # The only difference between the three dataframes is subj/child
    if 'subj' in tokens_df.columns:
        sort_by[sort_by.index('child')] = 'subj'
    return tokens_df.sort_values(sort_by).reset_index(drop=True)


def _calculate_listened_time(top3_top4_surplus_regions, month):
    """
    This uses a different definition of listened time than calculate_listened_time. The definition here is the sum of
    durations of top 3 (months 14-17) or top 4 (months 06-13) subregions.
    :param top3_top4_surplus_regions: the output of _get_top3_top4_surplus_regions
    :param month: month, str or int - both will do
    :return: int, listened time in ms
    """
    if 6 <= int(month) <= 13:
        top_x_kind = TOP_4_KIND
    elif 14 <= int(month) <= 17:
        top_x_kind = TOP_3_KIND
    else:
        raise ValueError(f'Invalid month: {month}')

    listened_time = (top3_top4_surplus_regions
                     .loc[lambda df: df.kind.eq(top_x_kind)]
                     .assign(duration=lambda df: df.end - df.start)
                     .duration.sum())

    return listened_time


# TODO: return namedtuple, returning a heterogeneous tuple has and will lead to errors
def gather_recording_nouns_audio(subject, month, recording_basic_level):
    """
    Gathers all the data needed to update seedlings_nouns for one audio recording.

    :param subject: subject id, e.g. '01'
    :param month: month, e.g. '08'
    :param recording_basic_level: the rows of all_basic_level that correspond to the recording
    :return: (top3/top4/surplus regions,
              recording_basic_level with is_top3/is_top4/is_surplus added,
              LENA recordings,
              total recorded time,
              total listened time)
    """
    # Sub-recordings and time totals
    lena_sub_recordings, duration_ms = get_lena_sub_recordings(recording_id=f'{AUDIO}_{subject}_{month}',
                                                               amend_if_special_case=True)

    # Regions

    # Remove subregions that weren't annotated in full, cuts silences and skips out of the regions, etc.
    processed_regions = get_processed_audio_regions(subject, month, amend_if_special_case=True)

    # Trim regions that end after duration_ms. One reason is that the subregion selection was done under assumption that
    # intervals in the 5min.csv files are 5 minutes long which isn't correct because they are actually 5 minutes of
    # clock time.
    processed_regions.loc[lambda df: df.end > duration_ms, 'end'] = duration_ms

    subregions = processed_regions.loc[lambda df: df.region_type.eq(RegionType.SUBREGION.value)]
    top3_top4_surplus_regions = _get_top3_top4_surplus_regions(processed_regions=processed_regions, month=month,
                                                               duration_ms=duration_ms)
    seedlings_nouns_regions = pd.concat([subregions,
                                         top3_top4_surplus_regions.rename(columns={'kind': 'region_type'})],
                                        axis='rows', ignore_index=True)

    # Remove subregions ranked 5 from months 06 and 07. They were need for _get_top3_top4_surplus_regions but should
    # not be used for assigning tokens to subregions. We are not doing it for the other months because they shouldn't
    # contain any subregions ranked 5 anyway.
    if month in ('06', '07'):
        seedlings_nouns_regions = seedlings_nouns_regions.loc[
            lambda df_: ~(df_.region_type.eq(RegionType.SUBREGION.value)
                          & df_.subregion_rank.eq(5))]

    # Add is_top_3_hours, is_top_4_hours, is_surplus to global_basic_level_for_recording
    tokens_assigned = assign_tokens_to_regions(tokens=recording_basic_level,
                                               seedlings_nouns_regions=seedlings_nouns_regions,
                                               month=month)
    # Add assignment columns to recording_basic_level
    recording_seedlings_nouns = (recording_basic_level
                                 .merge(tokens_assigned, on='annotid', how='inner')
                                 .pipe(_sort_tokens))

    # calculate_listened_time defines listened time as
    # - recording duration minus silence time for months 06 and 07 since they were otherwise annotated in full,
    # - sum of durations of planned-to-annotate subregions (ranked 1-4 for 08-13, ranked 1-3 for 14-17), makeup and
    #   extra regions for months 08-17.
    #
    # The listened time definition above worked when we were checking if we have enough time annotated in all recordings
    # but creates an inconsistency here: surplus is included in listened time for month 06-07 but excluded for 08-17.
    # So, for the seedlings-nouns dataset, we are going to redefine listened time as sum of top 4 (months 06-13) or top
    # 3 (months 14-17) subregions. This way, for all months, we have 3/4 hours of listened time and everything else
    # is surplus
    listened_ms = _calculate_listened_time(top3_top4_surplus_regions=top3_top4_surplus_regions, month=month)

    surplus_ms = calculate_total_surplus_time_ms(processed_regions=seedlings_nouns_regions)

    # Let's double-check that the two ways to calculate listened time are consistent
    listened_ms_old = calculate_listened_time(processed_regions=processed_regions, month=month,
                                              recordings=lena_sub_recordings)
    if month in ('06', '07'):
        assert listened_ms == listened_ms_old - surplus_ms
    else:
        assert listened_ms == listened_ms_old

    # Enforce column order
    def _enforce_column_order(df, dtypes):
        # At the recording level there is no recording_id
        columns = [column for column in dtypes if column != 'recording_id']
        return df[columns]

    recording_seedlings_nouns = _enforce_column_order(df=recording_seedlings_nouns,
                                                      dtypes=SEEDLINGS_NOUNS_DTYPES)
    seedlings_nouns_regions = _enforce_column_order(df=seedlings_nouns_regions,
                                                    dtypes=SEEDLINGS_NOUNS_REGIONS_LONG_DTYPES)
    lena_sub_recordings = _enforce_column_order(df=lena_sub_recordings,
                                                dtypes=SEEDLINGS_NOUNS_SUB_RECORDINGS_DTYPES)

    durations = pd.DataFrame.from_dict(dict(
        listened_ms=[listened_ms],
        surplus_ms=[surplus_ms],
        duration_ms=[duration_ms])
    )

    # Check that there are no subregions ranked 5 left. I removed and then added them too many times. :facepalm:
    def no_subregion_rank_5(series):
        return (series.isna() | series.isin([1, 2, 3, 4])).all()

    assert no_subregion_rank_5(seedlings_nouns_regions.subregion_rank)
    assert no_subregion_rank_5(recording_seedlings_nouns.subregion_rank)

    return (recording_seedlings_nouns,
            seedlings_nouns_regions,
            lena_sub_recordings,
            durations)


def load_video_recordings_csv(anonymize=True):
    """
    Loads the video recordings csv from BLab share.
    :return: a dataframe with the video recordings
    """
    video_info_df = read_video_recordings_csv()

    # Change start dates to happen on the same date. Shift end dates by the same deltas.
    if anonymize:
        # .dt.normalize() sets the time to 00:00:00, effectively extracting the date
        deltas = video_info_df.start.dt.normalize() - np.datetime64(ANONYMIZATION_DATE)
        video_info_df = video_info_df.assign(start=lambda df: df.start - deltas,
                                             end=lambda df: df.end - deltas)

    return video_info_df


def get_video_times(subject, month):
    """
    Gets the time of day of start and end, and duration times for a given subject and month.

    :param subject: subject id, e.g. '01'
    :param month: month, e.g. '08'
    :return: start_dt, end_dt, duration_ms
    """
    subject, month = _normalize_child_month(child=subject, month=month)
    subject_month = f'{subject}_{month}'
    video_recordings_info = load_video_recordings_csv(anonymize=True)
    ((start_dt, end_dt, duration),) = video_recordings_info.loc[lambda df: df.subject_month == subject_month,
                                                                ['start', 'end', 'duration']].values
    duration_ms = duration.total_seconds() * 1000

    return start_dt, end_dt, duration_ms


def gather_recording_nouns_video(subject, month, recording_basic_level):
    """
    Gathers all the data needed to update seedlings_nouns for one video recording.

    :param subject: subject id, e.g. '01'
    :param month: month, e.g. '08'
    :param recording_basic_level: the rows of all_basic_level that correspond to the recording
    :return: (recording_basic_level as is - new columns are only added for audio recordings,
              top3/top4/surplus regions (None because video),
              sub-recordings (a single one because video),
              total recorded time,
              total listened time)
    """
    start_dt, end_dt, duration_ms = get_video_times(subject, month)
    sub_recordings_df = pd.DataFrame.from_dict(dict(start_dt=[start_dt],
                                                    end_dt=[end_dt],
                                                    start_ms=[0],
                                                    end_ms=[duration_ms]))

    durations = pd.DataFrame.from_dict(dict(
        listened_ms=[duration_ms],
        surplus_ms=[0],
        duration_ms=[duration_ms])
    )

    return recording_basic_level, None, sub_recordings_df, durations


def gather_recording_seedlings_nouns(recording_id, recording_basic_level):
    """
    Gathers all the data needed to update seedlings_nouns for one recording.

    :param recording_id: full recording id, e.g. 'Video_01_16'
    :param recording_basic_level: the rows of all_basic_level that correspond to the recording
    :return: (top3/top4/surplus regions,
              recording_basic_level with is_top3/is_top4/is_surplus added,
              LENA recordings,
              total recorded time in ms,
              total listened time in ms)
    """
    modality, subject, month = split_recording_id(recording_id)

    if modality == VIDEO:
        return gather_recording_nouns_video(subject, month, recording_basic_level)
    elif modality == AUDIO:
        return gather_recording_nouns_audio(subject, month, recording_basic_level)
    else:
        raise ValueError(f'Unknown modality {modality} for recording {recording_id}')


def _preprocess_all_basic_level(all_basic_level_df):
    """
    Preprocess global basic level for seedlings_nouns
    :param all_basic_level_df:
    :return:
    """
    all_basic_level_preprocessed = (
        all_basic_level_df
        .drop(columns=['id', 'tier'])
        .rename(columns={'SubjectNumber': 'subject_month',
                         'pho': 'transcription',
                         'subj': 'child',
                         'global_bl': 'global_basic_level'})
        .assign(recording_id=lambda df: df.audio_video.str.capitalize() + '_'
                                        + df.child.astype(str) + '_'
                                        + df.month.astype(str))
        .pipe(_sort_tokens))

    return all_basic_level_preprocessed


def _gather_corpus_seedlings_nouns(all_basic_level_df):
    """
    Create all the csvs for the seedlings-nouns dataset
    :param all_basic_level_df: all_basiclevel dataframe
    :return: None
    """
    all_bl = _preprocess_all_basic_level(all_basic_level_df=all_basic_level_df)

    # Gather data for each recording and put into lists
    print('Processing video recordings is very quick, audio recordings take time.')
    everything = [
        (recording_id,) +
        gather_recording_seedlings_nouns(
            recording_id,
            # So that all the dataframes are later concatenated in the same way: with new column "recording_id" added.
            recording_basic_level=recording_tokens.drop(columns='recording_id'))
        for modality, modality_tokens in all_bl.groupby('audio_video', sort=False, observed=True)
        for recording_id, recording_tokens in tqdm(modality_tokens.groupby('recording_id', sort=False),
                                                   desc=f'Processing {modality} tokens')]
    (recording_ids,
     all_seedlings_nouns,
     all_regions,
     all_sub_recordings,
     all_durations) = zip(*everything)

    # Aggregate the lists into dataframes
    def _merge(dfs, dtypes, sort_by):
        concatenated = (pd.concat(objs=dfs,
                                  keys=recording_ids,
                                  names=['recording_id', 'sub_df_index'])
                        .reset_index('recording_id', drop=False)
                        .reset_index(drop=True))
        concatenated.recording_id = concatenated.recording_id.astype(pd.StringDtype())

        return concatenated.astype(dtypes).sort_values(by=sort_by).reset_index(drop=True)[dtypes.keys()]

    seedlings_nouns = _merge(all_seedlings_nouns,
                             dtypes=SEEDLINGS_NOUNS_DTYPES,
                             sort_by=SEEDLINGS_NOUNS_SORT_BY['seedlings-nouns.csv'])
    regions = _merge(all_regions,
                     dtypes=SEEDLINGS_NOUNS_REGIONS_LONG_DTYPES,
                     sort_by=SEEDLINGS_NOUNS_SORT_BY['regions.csv'])
    sub_recordings = _merge(all_sub_recordings,
                            dtypes=SEEDLINGS_NOUNS_SUB_RECORDINGS_DTYPES,
                            sort_by=SEEDLINGS_NOUNS_SORT_BY['sub-recordings.csv'])

    # The *_time columns will be added later - in _post_process_recordings
    recordings_dtypes = {column: dtype for column, dtype in SEEDLINGS_NOUNS_RECORDINGS_DTYPES.items()
                         if not column.endswith('_time')}
    recordings = _merge(all_durations,
                        dtypes=recordings_dtypes,
                        sort_by=SEEDLINGS_NOUNS_SORT_BY['recordings.csv'])

    return seedlings_nouns, regions, sub_recordings, recordings


def _make_updated_codebook(df, old_codebook_path):
    """
    Creates a new codebook for a dataframe and merges it with the old one if it exists.
    :param df: the dataframe
    :param old_codebook_path: path to the old codebook (doesn't have to exist)
    :return: codebook,
             is_new_dataframe (no old codebook),
             has_new_columns (some columns are new and missing descriptions)
    """
    codebook_template = make_codebook_template(df)

    # Merge with the old codebook
    if old_codebook_path.exists():
        codebook_template = codebook_template.drop(columns='description')
        # Load manually update columns from the old codebook
        auto_generated_columns = set(codebook_template.columns)
        codebook_template = codebook_template.merge(
            read_seedlings_codebook(old_codebook_path).drop(columns=auto_generated_columns - {'column'}),
            on='column', how='left')

    n_vars_without_description = codebook_template.description.isna().sum()
    n_vars = codebook_template.shape[0]
    has_new_columns = 0 < n_vars_without_description < n_vars
    is_new_dataframe = n_vars_without_description == n_vars

    return codebook_template, is_new_dataframe, has_new_columns


def _write_df_and_codebook(df, df_filename, output_dir, old_seedlings_nouns_csv_dir):
    """
    For a given dataframe,
    - creates/updates a codebook for it,
    - writes the dataframe to a csv,
    - writes the codebook to a csv.
    :param df: The dataframe.
    :param df_filename: Filename to use for the csv with the dataframe. Existing codebook will only be discovered if the
    filename hasn't changed since the last update. Rename the files in the seedlings-nouns_private repo first if you
    want new names.
    :param output_dir: where to save the csv files
    :param old_seedlings_nouns_csv_dir: where to look for the old codebook
    :return: (where the new codebook was saved - path to the new file,
              is this a new dataframe (no old codebook),
              are there new columns (some columns are new and missing descriptions))
    """
    # Paths
    new_df_path = output_dir / df_filename
    new_codebook_path = new_df_path.with_suffix('.codebook.csv')
    old_codebook_path = old_seedlings_nouns_csv_dir / new_codebook_path.name

    # New codebook
    codebook, is_new_dataframe, has_new_columns = _make_updated_codebook(df, old_codebook_path)

    # Save
    df.pipe(blab_write_csv, new_df_path)
    codebook.pipe(blab_write_csv, new_codebook_path)

    return new_codebook_path, is_new_dataframe, has_new_columns


def _print_seedlings_nouns_update_instructions(new_dataframes, new_variables,
                                               new_seedlings_nouns_csvs_dir):
    if new_dataframes:
        print('These dataframes never had a codebook and need their "description" column filled:\n'
              + '\n'.join(str(path) for path in new_dataframes))

    if new_variables:
        print('These dataframes have some new variables without description:\n'
              + '\n'.join(str(path) for path in new_variables))

    # Instructions
    step0 = ''
    if new_dataframes or new_variables:
        step0 = '0. Check whether the lists above correspond to what you expected.\n\n'

    new_dir_path = new_seedlings_nouns_csvs_dir.absolute()
    steps = (f'1. Copy the csv files and the log to a clone of bergelsonlab/seedlings-nouns_private.\n'
             f'   Do not use BLAB_DATA for this, make an extra clone if you haven\'t yet. We\'ll use\n'
             f'   $SN_PRIVATE to refer to the root of that clone below.\n\n'
             f'   from: {new_dir_path}\n'
             f'   to:   $SN_PRIVATE/blabpy_output/\n\n'
             f'2. Go to $SN_PRIVATE and follow the instructions in CONTRIBUTING.md to finish updating the dataset.\n')

    print(step0 + steps)

# TODO: This should be all done at the recording level - in gather_recording_seedlings_nouns
def _post_process_regions(regions):
    """
    Does a couple of things that should have been done at the recording level, but I couldn't figure out how to do it
    without breaking the code. Which means that the code is probably not very good and should be refactored. Here's
    what it does:
    - Reformats the table to make it more readable. See reformat_seedlings_nouns_regions.
    - Renames some columns and enforce column order. It already happened to regions but now - after reforamtting - it
      has to be done again.
    :param regions: regions in long format that come out of _gather_corpus_seedlings_nouns
    :return: non-overlapping regions as a wide table
    """
    # Make regions more readable, enforce column order, remove subregions ranked 5 from months 06 and 07. For other
    # months, subregions ranked 5 disappear in the beginning - when we process regions from the cha files). For months
    # 06 and 07 we keep them to use for makeup.
    regions = regions.copy()

    # Check that no rank-5 subregions remain
    assert not regions.loc[lambda df_:
                           df_.region_type.eq(RegionType.SUBREGION.value)
                           & df_.subregion_rank.eq(5)].shape[0] > 0

    # Make regions wide and nice
    regions = reformat_seedlings_nouns_regions(regions)

    # Enforce column order and update names - for consistency with seedlings-nouns.csv. Another thing that should have
    # been done upstream but it is easier to apply at the very end.
    return (regions
            .rename(columns={'is_top_3': 'is_top_3_hours',
                             'is_top_4': 'is_top_4_hours'})
            .loc[:, list(SEEDLINGS_NOUNS_REGIONS_WIDE_DTYPES.keys())])


def _post_process_recordings(recordings):
    """
    Add human-readable hh::mm::ss columns to recordings.
    :param recordings: Recordings dataframe output by _gather_corpus_seedlings_nouns.
    :return: Input dataframe with the new columns added
    """
    def ms_to_hms(series):
        # Check that no recording is longer than 24 hours because the conversion can only output time below that
        assert (series < 24 * 60 * 60 * 1000).all()
        return (series
                .pipe(pd.to_datetime, unit='ms')
                .dt.round('1s')
                .dt.strftime('%H:%M:%S'))

    # For each column whose name ends with "_ms", add a human-readable column that ends with _time
    for column in recordings.columns:
        if column.endswith('_ms'):
            recordings[column.replace('_ms', '_time')] = ms_to_hms(recordings[column]).astype('string')

    # Enforce column order
    recordings = recordings[SEEDLINGS_NOUNS_RECORDINGS_DTYPES.keys()]

    return recordings


def _make_updated_seedlings_nouns(all_basic_level_path, seedlings_nouns_csvs_dir, output_dir=Path()):
    """
    Write all the csvs and their codebooks to a given folder based on a csv with global basic level data and a folder
    that contains existing codebooks.
    :param all_basic_level_path: all_basiclevel_NA.csv path
    :param seedlings_nouns_csvs_dir: path to the folder containing the existing codebooks
    :param output_dir: where to write the new csvs and codebooks
    :return: path of the output folder
    """
    # Gather and write data
    all_basic_level_df = read_all_basic_level(all_basic_level_path)
    seedlings_nouns, regions, sub_recordings, recordings = _gather_corpus_seedlings_nouns(
        all_basic_level_df
        # .loc[lambda df: True
        #      & df.month.isin(['06', '07'])
        #      & df.subj.isin(['08', '25'])
        #      & df.audio_video.isin(['Audio'])
        #      ]
    )
    # pickle_file = 'seedlings_nouns_tables.pkl'
    # import pickle
    # with open(pickle_file, "wb") as f:
    #     pickle.dump((seedlings_nouns, regions, sub_recordings, recordings), f)
    # with open(pickle_file, "rb") as f:
    #     seedlings_nouns, regions, sub_recordings, recordings = pickle.load(f)

    regions = _post_process_regions(regions)
    recordings = _post_process_recordings(recordings)

    new_dataframes = []
    new_variables = []
    for df, filename in [(seedlings_nouns, 'seedlings-nouns.csv'),
                         (regions, 'regions.csv'),
                         (sub_recordings, 'sub-recordings.csv'),
                         (recordings, 'recordings.csv')]:
        new_codebook_path, is_new_dataframe, has_new_columns = _write_df_and_codebook(df, filename, output_dir,
                                                                                      seedlings_nouns_csvs_dir)
        if has_new_columns:
            new_variables.append(new_codebook_path)
        if is_new_dataframe:
            new_dataframes.append(new_codebook_path)

    # Print instructions
    _print_seedlings_nouns_update_instructions(new_dataframes=new_dataframes, new_variables=new_variables,
                                               new_seedlings_nouns_csvs_dir=output_dir)


def make_updated_seedlings_nouns():
    """Creates updated versions of all seedlings-nouns csvs.

    For this function to work, the following must be true:

    - You are connected to BLab share.
    - `all_basiclevel` is cloned to `~/BLAB_DATA/all_basiclevel`.
    - `seedlings-nouns_private` is cloned to `~/BLAB_DATA/seedlings-nouns_private`.
    - You are either (a) in the csvs folder of `seedlings-nouns_private` or (b) any other folder.
      - If it is (a), the working tree must be clean. The new csvs will overwrite the old ones in place, and you'll
        be instructed to commit the changes.
      - If it is (b), cwd must be empty. You'll be instructed to copy the new csvs to the repo before committing them.
    """
    # Get the newest version of all_basiclevel_NA.csv
    all_basic_level_path, abl_version = get_file_path(dataset_name='all_basiclevel',
                                                      version=None,
                                                      relative_path='all_basiclevel_NA.csv',
                                                      return_version=True)

    # Use the newest version of seedlings-nouns_private and make sure it's clean
    seedling_nouns_repo, _ = switch_dataset_to_version('seedlings-nouns_private', version=None)
    seedlings_nouns_csvs_dir = Path(seedling_nouns_repo.working_dir) / 'public'
    if seedling_nouns_repo.is_dirty():
        raise ValueError(f'There are unsaved changes in the seedlings-nouns_private repo. Please commit, stash, or '
                         'discard them. Find the repo here:\n'
                         f'{seedlings_nouns_csvs_dir.absolute()}')

    # If we're not working from the repo, we don't want to overwrite existing csvs in case we're in the wrong folder,
    # we want to keep the results of the previous run, etc. So, the current working directory should be empty.
    output_dir = Path.cwd()
    if output_dir.absolute() != seedlings_nouns_csvs_dir.absolute():
        if any(output_dir.iterdir()):
            raise ValueError(f'The current working directory is not empty. Please move to a different folder or '
                             'delete the files in this folder. Find the current working directory here:\n'
                             f'{output_dir.absolute()}')

    _make_updated_seedlings_nouns(all_basic_level_path, seedlings_nouns_csvs_dir, output_dir)

    # Log currently installed blabpy version and all_basiclevel versions

    # Using pip in case of editable installs where the version has not been updated yet
    pip_freeze = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE, text=True)
    versions = pip_freeze.stdout.split('\n')
    blabpy_version = next(version for version in versions if 'blabpy' in version)

    with output_dir.joinpath('log.txt').open('w') as log:
        log.write(f'blabpy version: {blabpy_version}\n')
        log.write(f'all_basiclevel version: {abl_version}\n')
