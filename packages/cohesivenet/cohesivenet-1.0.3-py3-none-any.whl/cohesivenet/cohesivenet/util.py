import json
import math
import os
import time
import re

from contextlib import contextmanager
from typing import Dict, List


def take(iterator, count):
    return [next(iterator) for _ in range(count)]


def take_keys(keys: List[str], data_dict: Dict):
    """Take keys from dict

    Arguments:
        keys {List[str]} -- Keys it include in output dict
        data_dict {Dict}

    Returns:
        [Dict]
    """
    return {k: v for k, v in data_dict.items() if k in keys}


def flatten_dict(d, prefix=None, joinchar="__"):
    """flatten_dict Flatten nested dictionary, joining paths into single string key

    Arguments:
        d {[type]} -- [description]

    Keyword Arguments:
        prefix {str} -- Prefix string for joining keys (default: {None})
        joinchar {str} -- String for joining nested keys (default: {'__'})

    Returns:
        [Dict] -- Dict of depth 1
    """
    key_value_pairs = {}

    def _prefix(k):
        return k if not prefix else "%s%s%s" % (prefix, joinchar, k)

    for k, v in d.items():
        if type(v) is dict:
            key_value_pairs.update(
                flatten_dict(v, prefix=_prefix(k), joinchar=joinchar)
            )
        else:
            key_value_pairs[_prefix(k)] = v
    return key_value_pairs


def unflatten_dict(d, splitchar="__"):
    """unflatten_dict Build nested dictionary based on keys

    Arguments:
        d {Dict}

    Keyword Arguments:
        splitchar {str} -- str marking nested dictionary (default: {'__'})

    Returns:
        [Dict]
    """
    resp = {}
    for flatkey, v in d.items():
        keyparts = flatkey.split(splitchar)
        _target = resp
        final_key = keyparts[-1]
        for key in keyparts[:-1]:
            if key not in _target:
                _target[key] = {}
            _target = _target[key]
        _target[final_key] = v
    return resp


def map_type(s, expected_type, strict=True):
    _def_return_val = s
    try:
        if type(s) is list:
            return s
        elif "list" in str(expected_type).lower():
            _def_return_val = []
            return json.loads(s)
        elif not s or s.lower() in ("none", ""):
            return None
        elif expected_type is bool:
            return s.lower() == "true"

        return expected_type(s)
    except ValueError:
        if not strict:
            return _def_return_val
        raise


def is_formattable_string(s):
    if type(s) not in (str, bytes):
        return False

    matches = re.findall(r"{[A-Za-z0-9_\.\[\]]*}", s)
    if matches:
        return [m.strip("{}") for m in matches]
    return False


def format_string(s, state):
    err_none = None
    if is_formattable_string(s):
        try:
            return s.format(**state), err_none
        except KeyError as e:
            return (s, "String format error: missing state args %s" % ",".join(e.args))
    return s, err_none


def dumb_replace(s, value):
    if type(s) not in (str, bytes):
        return s
    return re.sub(r"{.*}", value, s)


def is_list_index(s):
    match = re.match(r"(.*)\[(\d+)\]", str(s))
    if match:
        return match.group(1), match.group(2)
    return False


def get_path(data_dict, key_path, fail=False):
    """get_path

    Arguments:
        data_dict {dict} -- [description]
        key_path {str or List of strings} -- a.b.c or ['a', 'b', 'c']

    Keyword Arguments:
        fail {bool} -- Raise exception if does not exist (default: {False})

    Raises:
        Exception: Generic not found exception

    Returns:
        [any] -- value at key path
    """
    DOES_NOT_EXIST = 'Path "%s" does not exist' % key_path
    _target = data_dict
    steps = key_path if type(key_path) is list else key_path.split(".")

    for step in steps:
        if type(_target) is not dict:
            if fail:
                raise Exception(DOES_NOT_EXIST)
            return None

        step_list_index = is_list_index(step)
        list_index = None
        if step_list_index:
            step, list_index = step_list_index

        if step not in _target:
            if fail:
                raise Exception(DOES_NOT_EXIST)
            return None

        _target = _target.get(step)
        if list_index is not None:
            if type(_target) not in (list, tuple) or len(_target) <= int(list_index):
                if fail:
                    raise Exception(DOES_NOT_EXIST)
                return None
            _target = _target[int(list_index)]

    return _target


def map_dict_values(func_map, data_dict):
    return {k: func_map.get(k, lambda x: x)(v) for k, v in data_dict.items()}


def map_dict_keypaths(key_map, data_dict):
    updates = {
        new_key: get_path(data_dict, key_path) for key_path, new_key in key_map.items()
    }
    return {**data_dict, **updates}


def partition_list_groups(object_list, number_partitions):
    """Partition list of objects into groups

    Arguments:
        object_list {List[Any]}
        number_partitions {int} -- [description]

    Returns:
        [List[List[Any]]]
    """
    if number_partitions <= 1:
        return object_list

    object_count = len(object_list)
    partition_size = math.floor(object_count / number_partitions)
    leftovers = object_count % number_partitions
    leftover_set = object_list[-leftovers:] if leftovers else []
    rounded_list = object_list[:-leftovers] if leftovers else object_list

    return [
        rounded_list[i * partition_size : (i + 1) * partition_size]
        + ([leftover_set[i]] if len(leftover_set) > i else [])
        for i in range(number_partitions)
    ]


def partition_list_ratios(object_list, partition_ratios):
    """Partition list of objects into groups based on ratios list

    Arguments:
        object_list {List[Any]}
        partition_ratios {List[float]}

    Returns:
        Dict[str, List[Any]] - {
            '0.45': [...],
            '0.25': [...],
            '0.30': [...]
        }
    """
    assert math.isclose(sum(partition_ratios), 1.0), "Ratios must sum to 1"

    number_partitions = len(partition_ratios)
    if number_partitions <= 1:
        return object_list

    partition_sizes = [round(r * len(object_list)) for r in partition_ratios]
    _cursor = 0
    partitions = {}
    for i, size in enumerate(partition_sizes):
        partitions[str(partition_ratios[i])] = object_list[_cursor : (_cursor + size)]
        _cursor += size
    return partitions


def random_timestamp_filename(file_type=None):
    timestr = str(time.time()).replace(".", "_")
    if file_type:
        return "%s.%s" % (timestr, file_type)
    return timestr


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def version_dot_to_int(version_str):
    """version_dot_to_int

    Convert version dot string to comparable int.
    Examples:
        6 => 60000
        5.2 => 50200
        5.x.13 => 59913

    Args:
        version_str (str): str

    Returns:
        int
    """
    if type(version_str) is int:
        return version_str

    if version_str == "":
        return 0

    # 5.0, 5.2.1, 4.11.3
    parts = version_str.split(".")
    version_padded = ""
    num_parts = len(parts)
    if num_parts < 3:
        for _ in range(3 - num_parts):
            parts.append("0")

    assert len(parts) == 3, "version_str must have maximum of 3 parts delimited by '.'"
    for part in parts:
        if part.lower() == "x":
            part = "99"
        padded = "".join(["0" for _ in range(2 - len(part))]) + part
        version_padded += padded
    return int(version_padded)


def version_in_range(version_str, version_range):
    """Check if version string in range

    Args:
        version_str (str):
        version_range (list or str): can be list of version strings or string
            with "-" delimiter. e.g. "4.8.4-4.9.2"

    Returns:
        Boolean
    """
    version = version_dot_to_int(version_str)

    if type(version_range) is str:
        range_parts = version_range.split("-")
    else:
        assert type(version_range) is list
        range_parts = version_range

    range_parts_ints = [version_dot_to_int(p) for p in range_parts]
    total_range_parts = len(range_parts_ints)
    if total_range_parts != 2:
        return version in [p for p in range_parts_ints if p is not None]

    if range_parts_ints[0] == 0:
        # -Y.Y.Y means anything less than y.y.y inclusive
        return version <= range_parts_ints[1]
    elif range_parts_ints[1] == 0:
        # X.X.X- means anything more than x.x.x inclusive
        return range_parts_ints[0] <= version

    return range_parts_ints[0] <= version <= range_parts_ints[1]


def vapi_switch(fname, v1=None, v2=None):
    call_v1 = v1
    call_v2 = v2
    assert call_v1 or call_v2, "Must provide v1 or v2 methods"

    def vapi_call(api_client, *args, **kwargs):
        api_version = kwargs.pop("api_version", None)
        _api_version = api_version or api_client.api_version
        if not _api_version:
            if call_v2:
                return call_v2(api_client, *args, **kwargs)
            else:
                return call_v1(api_client, *args, **kwargs)
        elif _api_version == 2:
            return call_v2(api_client, *args, **kwargs)
        else:
            return call_v1(api_client, *args, **kwargs)

    vapi_call.__name__ = fname
    return vapi_call
