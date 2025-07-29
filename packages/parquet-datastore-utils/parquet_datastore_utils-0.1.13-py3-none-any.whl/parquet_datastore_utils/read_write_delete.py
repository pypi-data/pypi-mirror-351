from typing import List, Tuple, Union
import fsspec
import numpy as np
import datetime as dt
import pandas as pd
import pytz

import pyarrow as pa
import pyarrow.compute as pc
from pyarrow import parquet as pq, dataset as ds

from parquet_datastore_utils import cleaner


def get_merged_schema(dataset, schema=None):
    if schema is None:
        schema = dataset.schema
    for p in dataset.get_fragments():
        schema = pa.unify_schemas([schema, p.scanner().dataset_schema])
    return schema


def _create_schema(types_dict):
    schema = []
    for key, val in types_dict.items():
        if val in (dt.datetime, np.datetime64, pd.core.dtypes.dtypes.DatetimeTZDtype):
            schema.append((key, pa.timestamp('ns')))
        else:
            schema.append((key, pa.from_numpy_dtype(val)))

    return pa.schema(schema)


def _to_utc(d: dt.datetime) -> dt.datetime:
    """Return timezone-aware timestamp in UTC. Timezone-naive input is interpreted as UTC.
    """
    if d.tzinfo is None:
        return pytz.utc.localize(d)  # Timezone-naive: interpret as UTC
    return d.astimezone(pytz.utc)


def _index_to_utc(df: pd.DataFrame) -> pd.DataFrame:
    """Convert a pd.DataFrame index to UTC. If current index is timezone-naive, will be localized to UTC.

    Raises
    ------
    TypeError : If DataFrame index is not a DatetimeIndex.
    """
    if not len(df):
        return df
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(f'Expected DataFrame with a DatetimeIndex. You passed a {type(df.index)}.')

    if df.index.tzinfo is None:
        df.index = df.index.tz_localize(pytz.utc)
    else:
        df.index = df.index.tz_convert(pytz.utc)

    return df


def _index_metadata(dataset) -> Tuple[str, Union[str, None]]:
    """Return index name and index timezone
    """
    pd_meta = dataset.schema.pandas_metadata
    index_name = pd_meta['index_columns'][0]
    d = [d for d in pd_meta['columns'] if d['name'] == index_name][0]
    index_tz = None if d['metadata'] is None else d['metadata']['timezone']
    if index_tz is not None:
        if index_tz.lower() != "utc":
            raise ValueError(f'Internal error in parquet-datastore-utils: '
                             f'Expected data to be stored timezone-aware in UTC or timezone-naive, '
                             f'but got data stored in {index_tz}.')

    return index_name, index_tz


def write(data: pd.DataFrame,
          uri: str,
          partition_cols: list = None,
          overwrite_period: bool = False,
          ) -> None:
    """
    Writes a pandas DataFrame to parquet. For timeseries data, existing data within the time range of the new data can
    optionally be overwritten.

    Parameters
    ----------
    data: pandas.DataFrame
        The data to be written. Must have DatetimeIndex. If timezone-naive, UTC will be assumed.
    uri: str
        The destination to write the data to. Either a local file path or an fsspec style path like `file:///C:/data` or
        `s3://bucket/key`
    partition_cols: list, optional
        Columns to partition on
    overwrite_period: bool, optional
        Only applicable to timeseries data where there is existing data in the destination. If True, any chunks that
        overlap with the new data will be loaded, existing data in the interval covered by the new data will be removed,
        and the new data will be merged with any remaining data from those chunks. The result will then be written to
        `uri`. Only once the write is successful, all but the newest file in each partition directory will be removed,
        avoiding duplicate data in any given time period.
    """
    df = _index_to_utc(data)  # Always save data with timezone-aware timestamps in UTC
    keys = get_partition_keys(df, partition_cols)
    wait_until_released(keys)
    try:
        # Simple case, new dataset or relying on default behaviour
        if not fsspec.get_mapper(uri).fs.exists(uri) or not overwrite_period:
            df.to_parquet(uri, partition_cols=partition_cols)
            return

        new_table = pa.table(df)
        current_ds = pq.ParquetDataset(uri)

        update_tables = []
        for fragment in current_ds.fragments:
            parts = ds._get_partition_keys(fragment.partition_expression)
            if all([(df[key] == value).any() for key, value in parts.items()]):
                fragment_data = fragment.to_table()
                # append with partition values
                for key, value in parts.items():
                    value_array = pa.array(fragment_data.num_rows * [value], type=new_table[key].type)
                    fragment_data = fragment_data.append_column(key, value_array)
                update_tables.append(fragment_data)

        if len(update_tables) > 0:
            # Data overlaps data in existing fragments
            index_name = df.index.name
            existing_table = pa.concat_tables(update_tables, promote=True)
            existing_table = existing_table.set_column(existing_table.column_names.index(index_name), index_name,
                                                       existing_table[index_name].cast(new_table[index_name].type))
            data_before = existing_table.filter((pc.field(index_name) < df.index.min()))
            data_after = existing_table.filter((pc.field(index_name) > df.index.max()))
            out = pa.concat_tables([data_before, new_table, data_after],
                                   promote=True)  # Promote=True to allow for mismatched schemas
        else:
            out = new_table

        pq.write_to_dataset(out, uri, partition_cols=partition_cols)
        cleaner.keep_only_newest_in_dataset(current_ds)

    finally:
        release_lock(keys)
    return


def read(uri: str,
         columns: list = None,
         start_end: (dt.datetime, dt.datetime) = None,
         types_dict: dict = None,
         merge_schemas: bool = None,
         **kwargs) -> pd.DataFrame:
    """
    Reads a parquet dataset and returns a pandas dataframe. Optionally performing a schema merge to allow for schema
    evolution. Note that schema merges can be expensive, specifying an explicit schema with the `schema` kwarg or
    `types_dict` is likely to improve performance in the case that the column(s) you want have been added after initial
    dataset creation.

    Parameters
    ----------
    uri: str
        The URI of the dataset, either a local filepath, or any fsspec compliant path specification.
    columns: list, optional
        The columns to read from the dataset. Omit to read the whole dataset
    start_end: tuple with 2 dt.datetime variables, optional
        Specify a time period to read from the dataset. If timezone-naive, will be interpreted as UTC.
    types_dict: dict, optional
        A dictionary in the form {<field_name>: <type>} where type is a python or numpy type.
    merge_schemas: bool, optional
        Can take values True, False or None (default). If True, an attempt will always be made to merge the schemas of
        all fragments in the dataset. If None, the returned DataFrame will not be guaranteed to contain all columns that
        only appear in some fragments, if a column specified by the `columns` argument isn't found, a schema merge will
        be performed implicitly. If False, a schema merge will never be performed, and a pyarrow.lib.ArrowInvalid error
        will be raised if a column is not found. Schema merges can be expensive, depending on the number of fragments and
        the seek performance of the filesystem and media (i.e. they will be slower on spinning hard drives than SSDs).
    kwargs:
        Will be passed to the PyArrow parquet engine. The `schema` argument will be overwritten if types_dict is passed.
        If merge_schemas is True, a Schema specified with `schema` will be merged with those read from fragments.

    Returns
    -------
    pandas.Dataframe : stored data, with timezone-aware DatetimeIndex. Returns empty DataFrame if dataset is empty.

    Raises
    ------
    ValueError : If start > end, or if start_end is not None and dataset has no pandas metadata.
    """

    dataset = ds.dataset(uri)
    if not len(dataset.schema):
        return pd.DataFrame()

    if types_dict is not None:
        kwargs['schema'] = pa.unify_schemas([ds.dataset(uri).schema, _create_schema(types_dict)])

    if merge_schemas is True:
        kwargs['schema'] = get_merged_schema(dataset, kwargs.get('schema'))

    if start_end is not None:
        if b'pandas' not in dataset.schema.metadata:
            raise ValueError('Cannot filter by DataFrame index: No pandas metadata found in dataset.')
        index_name, index_tz = _index_metadata(dataset)
        start_utc, end_utc = _to_utc(start_end[0]), _to_utc(start_end[1])
        if start_utc > end_utc:
            raise ValueError(f'Timestamp "start" must be equal or less than "end". You provided '
                             f'start={start_utc.isoformat()}, end={end_utc.isoformat()}.')

        filters = list(kwargs['filters']) if 'filters' in kwargs else []
        filters_using_index = [f[0] for f in filters if f[0] == index_name]
        if filters_using_index:
            raise ValueError(f'Invalid entry in "filters": Filtering by index column "{index_name}" not allowed. '
                             f'To read part of the dataset, use the "start_end" argument of the read() method.')

        # If data have been stored timezone-naive (for some reason, old data etc.), filter by timezone-naive
        if index_tz is None:
            start_utc, end_utc = start_utc.replace(tzinfo=None), end_utc.replace(tzinfo=None)

        filters.append((index_name, '>=', start_utc))
        filters.append((index_name, '<=', end_utc))
        kwargs['filters'] = filters

    def read_df() -> pd.DataFrame:
        df = pd.read_parquet(uri, columns=columns, **kwargs)
        # Data was stored in timezone-aware UTC. In case we had old data stored timezone-naive, return timezone-aware.
        df = _index_to_utc(df)
        return df

    try:
        return read_df()
    except pa.lib.ArrowInvalid:
        if merge_schemas is None or True:
            kwargs['schema'] = get_merged_schema(dataset, kwargs.get('schema'))
        else:
            raise

    return read_df()


def delete_between(uri: str,
                   start: dict,
                   end: dict,
                   partition_cols: List[str] = None,
                   ) -> None:
    """
    Delete data within a specified date range from a Parquet dataset.

    Parameters:
    ----------
    uri : str
        The URI of the dataset, either a local filepath, or any fsspec compliant path specification.
    start, end : dict
        The start / end timestamp of the date range to delete. Both are inclusive.
        Dict keys are "timestamp" (start / end timestamps) and a value for each of the partition_cols.
        If timezone-naive, "timestamp" is interpreted as UTC.
        Example: If partition_cols is ['year', 'quarter'], then start could look like
        {"timestamp": d, "year": dd.year, "quarter": dd.quarter}, with
        d = dt.datetime.fromisoformat('2017-05-10 00:00:00+01:00'), dd=pd.to_datetime(d)
    partition_cols : list, optional
        Columns to partition on, if the dataset is partitioned.

    Raises
    ------
    ValueError : If start and/or end are malformed (see docstring above) or start > end.

    Notes
    -----
    - This assumes that data have been stored in UTC, as timezone-aware timestamps.
    """

    for k in partition_cols:
        if k not in start or k not in end:
            raise ValueError(f'The provided "start" and "end" dictionaries must contain a value '
                             f'for each of the partition columns. Value missing for "{k}".')
    if 'timestamp' not in start or 'timestamp' not in end:
        raise ValueError(f'The provided "start" and "end" dictionaries must contain a key "timestamp".')

    start_utc, end_utc = _to_utc(start['timestamp']), _to_utc(end['timestamp'])
    if start_utc > end_utc:
        raise ValueError(f'Timestamp "start" must be equal or less than "end". You provided '
                         f'start={start_utc.isoformat()}, end={end_utc.isoformat()}.')

    dataset = pq.ParquetDataset(uri)

    if partition_cols is None:
        in_between = []
        overlapping = dataset.fragments
    else:
        # Assign tuple with partition information to each fragment
        partition_info = dict()
        for fragment in dataset.fragments:
            parts = ds._get_partition_keys(fragment.partition_expression)
            partition_info[fragment] = tuple(parts[x] for x in partition_cols)

        # Find fragments that are overlapping with start or end (to be filtered),
        # and the fragments that are completely in-between start and end (to be deleted).
        # All other fragments remain untouched.
        start_parts = tuple(start[x] for x in partition_cols)
        end_parts = tuple(end[x] for x in partition_cols)
        overlapping = [k for k, v in partition_info.items() if v == start_parts or v == end_parts]
        in_between = [k for k, v in partition_info.items() if start_parts < v < end_parts]
        # print(f'{len(in_between)} fragments in-between, {len(overlapping)} fragments overlapping.')

    # Filter overlapping fragments, write to disk, delete old fragment files
    if len(overlapping) > 0:
        # Append partition values to overlapping fragments
        overlapping_tables = []
        for fragment in overlapping:
            parts = ds._get_partition_keys(fragment.partition_expression)
            fragment_data = fragment.to_table()
            for key, value in parts.items():
                # value_array = pa.array(fragment_data.num_rows * [value], type=new_table[key].type)
                value_array = pa.array(fragment_data.num_rows * [value], type=dataset.schema.field(key).type)
                fragment_data = fragment_data.append_column(key, value_array)
            overlapping_tables.append(fragment_data)
        overlapping_table = pa.concat_tables(overlapping_tables, promote=True)

        # If data have been stored timezone-naive (for some reason, old data etc.), filter by timezone-naive
        index_name, index_tz = _index_metadata(dataset)
        if index_tz is None:
            start_utc, end_utc = start_utc.replace(tzinfo=None), end_utc.replace(tzinfo=None)

        data_before = overlapping_table.filter((pc.field(index_name) < start_utc))
        data_after = overlapping_table.filter((pc.field(index_name) > end_utc))
        out = pa.concat_tables([data_before, data_after],
                               promote=True)  # Promote=True to allow for mismatched schemas

        if len(out):
            pq.write_to_dataset(out, uri, partition_cols=partition_cols)
            cleaner.keep_only_newest_in_dataset(dataset)
        else:
            # No data left over after filtering -> delete
            cleaner.delete_fragments(overlapping)

    # Delete in-between fragments
    cleaner.delete_fragments(in_between)

    return


import time

MAX_CHECKS = 100
SLEEP_SECONDS = 0.2
global LOCKS
LOCKS = []


def wait_until_released(partition_keys):
    """Waits until all locks for the partition are dealt with, then locks partition keys.
    """
    for i in range(MAX_CHECKS):
        is_locked = check_is_locked(partition_keys)
        if not is_locked:
            break
        time.sleep(SLEEP_SECONDS)
    return do_lock(partition_keys)


def check_is_locked(partition_keys):
    """Queries if any of the partition keys is locked.
    """
    for key in partition_keys:
        if key in LOCKS:
            return True
    return False


def do_lock(partition_keys):
    """Registers the partition key as locked.
    """
    global LOCKS
    for key in partition_keys:
        LOCKS.append(key)
    return


def release_lock(partition_keys):
    """Removes the partition from the lock.
    """
    global LOCKS
    for key in partition_keys:
        try:
            LOCKS.remove(key)
        except:
            pass
    return


def get_partition_keys(data, partition_cols):
    """Extracts unique names based on the partition-related values in the data.
    """
    series = pd.Series(name='tmp', data='', index=data.index, dtype=str)
    for column in partition_cols:
        series = series + "-" + data[column].astype(str)
    keys = list(np.unique(series))

    return keys
