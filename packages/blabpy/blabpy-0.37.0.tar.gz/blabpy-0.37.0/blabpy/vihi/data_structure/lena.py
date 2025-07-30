"""
This module checks that the LENA folder contains all and only files that we expect to be there.
"""
import re
from enum import auto, unique
from pathlib import Path

import pandas as pd
from strenum import StrEnum

from ..paths import get_lena_annotations_path, compose_full_recording_id, parse_full_recording_id, \
    get_lena_recording_path, get_vihi_path

# Strings to match literally, and re.Pattern objects to match in the sense of re.match. Add $ to match the full name.
IGNORED = [re.compile(r'~.*\.docx$'), '.DS_Store', '.git']


@unique
class AuditStatus(StrEnum):
    ignored = auto()
    expected = auto()
    unexpected = auto()
    missing = auto()


def _name_matches(path, rule_list):
    """
    Checks if the name of the file at path matches any of the rules
    :param path:
    :param rule_list: a list of strings and re.Pattern objects to match against
    :return: rule_list element that the path name matched if there was a match, None if there were no matches
    """
    name = path.name
    for rule in rule_list:
        if isinstance(rule, str) and name == rule:
            return rule
        elif isinstance(rule, re.Pattern) and rule.match(name):
            return rule
    return


def audit_recording_folder(folder_path: Path, population: str, subject_id: str, recording_id: str):
    """
    Checks a recording folder for
    :param folder_path: path to the folder with the recording
    :param population: population
    :param subject_id: subject id string
    :param recording_id: recording id string
    :return: a dataframe with the status of each file in folder in `path`
    """
    assert folder_path.is_dir()
    full_recording_id = compose_full_recording_id(population, subject_id, recording_id)
    assert folder_path.name == full_recording_id

    expected_objects = [
        f'{full_recording_id}.eaf',
        f'{full_recording_id}.its',
        f'{full_recording_id}.wav',
        f'{full_recording_id}.pfsx',
        f'{full_recording_id}.upl',
        f'{full_recording_id}_lena5min.csv',
        f'VIHI_Coding_Issues_{full_recording_id}.docx'
    ]

    objects_statuses = list()
    satisfied_rules = list()
    folder_contents = [path.relative_to(folder_path) for path in folder_path.iterdir()]
    for path in folder_contents:
        if _name_matches(path, rule_list=IGNORED):
            objects_statuses.append(AuditStatus.ignored)
            continue

        rule_matched = _name_matches(path, rule_list=expected_objects)
        if rule_matched:
            satisfied_rules.append(rule_matched)
            objects_statuses.append(AuditStatus.expected)
        else:
            objects_statuses.append(AuditStatus.unexpected)

    missing_files = [rule for rule in expected_objects if rule not in satisfied_rules]
    audit_results = ([(path.as_posix(), str(status)) for path, status in zip(folder_contents, objects_statuses)]
                     + [(rule, str(AuditStatus.missing)) for rule in missing_files])

    return (pd.DataFrame(columns=['relative_path', 'status'], data=audit_results)
            .sort_values(by=['status', 'relative_path'])
            .reset_index(drop=True))


def audit_all_recordings():
    """
    Checks:
    - all the folders at levels between ".../LENA" and the recording-level folders,
    - all the recording-level folders using `audit_recording_folder`
    :return:
    """
    recordings_list = pd.read_csv(get_vihi_path().joinpath('vihi_data_check', 'recordings.csv'))
    recordings_list[['population', 'subject_id', 'recording_id']] = pd.DataFrame(
        recordings_list.recording.apply(parse_full_recording_id).to_list())

    # Check the folder presence at population, subject, and recording levels
    annotations_dir = get_lena_annotations_path()
    expected_folders = {
        folder
        for population, subject_id, recording_id
        in recordings_list[['population', 'subject_id', 'recording_id']].drop_duplicates().to_records(index=False)
        for folder in (
            annotations_dir / population,
            annotations_dir / population / f'{population}_{subject_id}',
            annotations_dir / population / f'{population}_{subject_id}' / f'{population}_{subject_id}_{recording_id}'
        )}

    actual_folders = {
        path
        for glob_results in (annotations_dir.glob('*'),
                             annotations_dir.glob('*/*'),
                             annotations_dir.glob('*/*/*'))
        for path in glob_results
        if path.is_dir()
    }

    folder_statuses = list()
    unexpected = actual_folders - expected_folders
    expected = actual_folders & expected_folders
    missing = expected_folders - actual_folders
    for folder_list, status in [(unexpected, AuditStatus.unexpected),
                                (expected, AuditStatus.expected),
                                (missing, AuditStatus.missing)]:
        for folder in folder_list:
            folder_statuses.append(dict(parent=annotations_dir,
                                        relative_path=folder.relative_to(annotations_dir), status=status))

    # Check the recording folders contents
    recordings_list['folder_path'] = recordings_list.apply(
        lambda row: get_lena_recording_path(row.population, row.subject_id, row.recording_id),
        axis='columns')
    recording_audits = recordings_list.apply(
        lambda row:
        audit_recording_folder(
            folder_path=row.folder_path,
            population=row.population,
            subject_id=row.subject_id,
            recording_id=row.recording_id).assign(parent=row.folder_path),
        axis='columns',
        result_type='reduce')

    # Combine the results
    full_results = pd.concat([pd.DataFrame(folder_statuses)] + recording_audits.to_list())
    assert full_results.columns.to_list() == ['parent', 'relative_path', 'status']

    # Sort by full path and convert "parent" to string
    full_results = (full_results
                    .assign(full_path=lambda df: df.parent / df.relative_path)
                    .sort_values(by='full_path')
                    .drop(columns='full_path')
                    .assign(parent=lambda df: df.parent.apply(lambda path: path.as_posix()))
                    )

    return full_results
