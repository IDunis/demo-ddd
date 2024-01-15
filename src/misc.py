"""
Various tool function for Freqtrade and scripts
"""
import gzip
import logging
from pathlib import Path
from typing import Any, TextIO, Union

import pandas as pd
import rapidjson


logger = logging.getLogger(__name__)


def file_dump_json(filename: Path, data: Any, is_zip: bool = False, log: bool = True) -> None:
    """
    Dump JSON data into a file
    :param filename: file to create
    :param is_zip: if file should be zip
    :param data: JSON Data to save
    :return:
    """

    if is_zip:
        if filename.suffix != '.gz':
            filename = filename.with_suffix('.gz')
        if log:
            logger.info(f'dumping json to "{filename}"')

        with gzip.open(filename, 'w') as fpz:
            rapidjson.dump(data, fpz, default=str, number_mode=rapidjson.NM_NATIVE)
    else:
        if log:
            logger.info(f'dumping json to "{filename}"')
        with filename.open('w') as fp:
            rapidjson.dump(data, fp, default=str, number_mode=rapidjson.NM_NATIVE)

    logger.debug(f'done json to "{filename}"')


def file_dump_joblib(filename: Path, data: Any, log: bool = True) -> None:
    """
    Dump object data into a file
    :param filename: file to create
    :param data: Object data to save
    :return:
    """
    import joblib

    if log:
        logger.info(f'dumping joblib to "{filename}"')
    with filename.open('wb') as fp:
        joblib.dump(data, fp)
    logger.debug(f'done joblib dump to "{filename}"')


def json_load(datafile: Union[gzip.GzipFile, TextIO]) -> Any:
    """
    load data with rapidjson
    Use this to have a consistent experience,
    set number_mode to "NM_NATIVE" for greatest speed
    """
    return rapidjson.load(datafile, number_mode=rapidjson.NM_NATIVE)


def file_load_json(file: Path):

    if file.suffix != ".gz":
        gzipfile = file.with_suffix(file.suffix + '.gz')
    else:
        gzipfile = file
    # Try gzip file first, otherwise regular json file.
    if gzipfile.is_file():
        logger.debug(f"Loading historical data from file {gzipfile}")
        with gzip.open(gzipfile) as datafile:
            pairdata = json_load(datafile)
    elif file.is_file():
        logger.debug(f"Loading historical data from file {file}")
        with file.open() as datafile:
            pairdata = json_load(datafile)
    else:
        return None
    return pairdata


def deep_merge_dicts(source, destination, allow_null_overrides: bool = True):
    """
    Values from Source override destination, destination is returned (and modified!!)
    Sample:
    >>> a = { 'first' : { 'rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            deep_merge_dicts(value, node, allow_null_overrides)
        elif value is not None or allow_null_overrides:
            destination[key] = value

    return destination
