import re
from pathlib import Path

from ..paths import get_blab_share_path


POPULATIONS = ['VI', 'HI', 'TD']


def get_vihi_path():
    """
    Finds the path to the VIHI folder on BLab share
    :return: Path object
    """
    return get_blab_share_path() / 'VIHI'


def get_subject_files_path():
    """
    Returns the path to the SubjectFiles folder within the VIHI folder
    :return: Path object
    """
    return get_vihi_path() / 'SubjectFiles'


def _get_modality_path(modality):
    """
    Return the path to a modality folder withing the SubjectFiles folder
    :return: Path object
    """
    return get_subject_files_path() / modality


def get_lena_path():
    """
    Returns the path to the LENA folder within the SubjectFiles folder
    :return: Path object
    """
    return _get_modality_path('LENA')


def get_lena_annotations_path():
    """
    Returns the path to the repo with annotations of LENA recordings.
    """
    return get_lena_path() / 'annotations'


def get_lena_annotations_in_progress_path():
    """
    Returns the path to the folder where the annotations should be manually updated.
    """
    return get_lena_path() / 'annotations-in-progress'


def _id_from_int(id_):
    """
    Converts integer subject and recordings ids to a 3-digit-long zero-paddes string
    :param id_: int
    :return: str
    """
    return f'{id_:03}'


def _check_id_string(id_):
    """
    Checks that the subject or recordings id is formatted correctly by converting to number and back.
    :param id_:
    :return:
    """
    assert isinstance(id_, str)
    assert _id_from_int(int(id_)) == id_


def _check_population(population):
    assert population in POPULATIONS


def compose_full_recording_id(population: str, subject_id: str, recording_id: str):
    """
    Combines population type, subject id, and recording id into a full recording id, e.g., VI_123_456
    :param population: VI/HI/TD
    :param subject_id:
    :param recording_id:
    :return:
    """
    _check_population(population)
    _check_id_string(subject_id)
    _check_id_string(recording_id)
    return f'{population}_{subject_id}_{recording_id}'


def parse_full_recording_id(full_recording_id):
    """
    Parse a full recording id, e.g., VI_123_456, into three constituent parts.
    :param full_recording_id: a string
    :return: a dict with string values and keys population, subject_id, recording_id
    """
    population, subject_id, recording_id = full_recording_id.split('_')
    _check_population(population)
    _check_id_string(subject_id)
    _check_id_string(recording_id)

    return dict(population=population, subject_id=subject_id, recording_id=recording_id)


def get_lena_population_path(population, lena_annotations_path=None):
    """
    Find the LENA population-level folder
    :param population: one of POPULATIONS
    :return: Path object
    """
    _check_population(population)
    lena_annotations_path = lena_annotations_path or get_lena_annotations_path()
    return Path(lena_annotations_path) / population


def get_lena_subject_path(population, subject_id, lena_annotations_path=None):
    """
    Find the LENA subject-level folder
    :param population: one of POPULATIONS
    :param subject_id: zero-padded three-digit string
    :return: Path object
    """
    _check_population(population)
    _check_id_string(subject_id)
    lena_population_path = get_lena_population_path(population, lena_annotations_path=lena_annotations_path)
    return lena_population_path / f'{population}_{subject_id}'


def get_lena_recording_path(population, subject_id, recording_id, assert_exists=False):
    """
    Find the LENA subject-level folder
    :param population: one of POPULATIONS
    :param subject_id: zero-padded three-digit string
    :param recording_id: --//--
    :param assert_exists: If True and the recording doesn't exist, raises FileNotFoundError
    :return: Path object
    """
    _check_population(population)
    _check_id_string(subject_id)
    _check_id_string(recording_id)

    subject_path = get_lena_subject_path(population=population, subject_id=subject_id)
    full_recording_id = compose_full_recording_id(population, subject_id, recording_id)
    recording_path = subject_path / full_recording_id

    if assert_exists and not recording_path.exists():
        raise FileNotFoundError(f'Couldn\'t find the recording folder at\n'
                                f'{recording_path}\n'
                                f'Double-check that {full_recording_id} is the correct ID.')

    return recording_path


def get_raw_data_dir():
    """
    Find the folder with the raw LENA files.
    """
    return get_lena_path() / 'rawish_data'


def get_its_dir():
    """
    Find the folder with the LENA .its files
    """
    return get_raw_data_dir() / 'its'


def get_its_path(population, subject_id, recording_id):
    """
    Find the .its file.
    :param population: one of POPULATIONS
    :param subject_id: zero-padded three-digit string
    :param recording_id: --//--
    :return: Path object
    """
    _check_population(population)
    _check_id_string(subject_id)
    _check_id_string(recording_id)
    full_recording_id = compose_full_recording_id(population, subject_id, recording_id)

    its_path = get_its_dir() / f'{full_recording_id}.its'

    return its_path


def get_rttm_path(population, subject_id, recording_id):
    """
    Find the .rttm file with the VTC output for a single recording.
    :param population: one of POPULATIONS
    :param subject_id: zero-padded three-digit string
    :param recording_id: --//--
    :return: Path object
    """
    _check_population(population)
    _check_id_string(subject_id)
    _check_id_string(recording_id)

    annotations_path = get_lena_annotations_path()
    full_recording_id = compose_full_recording_id(population, subject_id, recording_id)
    rttm_path = annotations_path / 'derivatives' / 'vtc' / 'separated' / full_recording_id / 'all.rttm'

    return rttm_path


def get_eaf_path(population, subject_id, recording_id, lena_annotations_path=None):
    """
    Find the .eaf file with the ACLEW-style annotations for a single recording.
    :param population: one of POPULATIONS
    :param subject_id: zero-padded three-digit string
    :param recording_id: --//--
    :return: Path object
    """
    _check_population(population)
    _check_id_string(subject_id)
    _check_id_string(recording_id)

    subject_dir = get_lena_subject_path(population, subject_id, lena_annotations_path=lena_annotations_path)
    assert subject_dir.exists(), 'Can\'t find the subject folder. Check the arguments.'

    full_recording_id = compose_full_recording_id(population, subject_id, recording_id)
    eaf_path = subject_dir / full_recording_id / f'{full_recording_id}.eaf'

    return eaf_path


def find_all_lena_recording_folders(lena_annotations_path=None, skip_excluded=False):
    """
    Find all LENA recording folders.
    :return: list of Path objects
    """
    def _extract_group(regex, string):
        match = re.match(regex, string)
        return match.group(1) if match else None

    if lena_annotations_path is not None:
        lena_annotations_path = Path(lena_annotations_path)
    else:
        lena_annotations_path = get_lena_annotations_path()

    recordings = []
    for population in POPULATIONS:
        population_dir = lena_annotations_path / population
        for subject_dir in population_dir.iterdir():
            if not subject_dir.is_dir():
                continue
            if skip_excluded and subject_dir.name.endswith('_excl'):
                continue

            subject_id = _extract_group(rf'{population}_(\d{{3}})', subject_dir.name)
            if subject_id:
                for recording_dir in subject_dir.iterdir():
                    if not recording_dir.is_dir():
                        continue
                    recording_id = _extract_group(rf'{population}_{subject_id}_(\d{{3}})', recording_dir.name)
                    if recording_id:
                        recordings.append(recording_dir)

    return recordings


def find_all_lena_recording_ids(lena_annotations_path=None, skip_excluded=False):
    """
    Find all LENA recording folders and return a list of full recording ids.
    See find_all_lena_recording_folders for the arguments.
    :return: list of strings
    """
    lena_recording_folders = find_all_lena_recording_folders(lena_annotations_path=lena_annotations_path,
                                                             skip_excluded=skip_excluded)
    return [folder.name for folder in lena_recording_folders]


def find_all_lena_eaf_paths(lena_annotations_path=None, skip_excluded=False):
    """
    Find all LENA .eaf files.
    See find_all_lena_recording_folders for the arguments.
    :return: list of Path objects
    """
    lena_recording_folders = find_all_lena_recording_folders(lena_annotations_path=lena_annotations_path,
                                                             skip_excluded=skip_excluded)
    return [folder / f'{folder.name}.eaf'
            for folder in lena_recording_folders]
