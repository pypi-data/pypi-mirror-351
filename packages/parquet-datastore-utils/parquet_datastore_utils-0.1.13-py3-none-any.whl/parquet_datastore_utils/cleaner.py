import os
from typing import List
import fsspec
import pyarrow.parquet as pq
import pyarrow as pa


def keep_only_newest_in_dataset(dataset: pq.ParquetDataset):
    """Delete fragment files for all fragments in dataset, keeping only the newest ones.
    """
    dirs = set([os.path.dirname(fragment.path) for fragment in dataset.fragments])
    for d in dirs:
        delete_all_except_newest(d)


def delete_all_except_newest(dir_: str):
    f = fsspec.get_mapper(dir_).fs
    if len(f.expand_path('{}/*'.format(dir_))) <= 1:
        return

    newest_mtime = 0
    for leaf in f.expand_path('{}/*'.format(dir_)):
        info = f.info(leaf)
        if info['mtime'] > newest_mtime:
            newest_mtime = info['mtime']
            newest_leaf = leaf

    deleted = []
    for leaf in f.expand_path('{}/*'.format(dir_)):
        if leaf != newest_leaf:
            f.rm(leaf)
            deleted.append(leaf)

    return deleted


def delete_fragments(fragments: List[pa.dataset.ParquetFileFragment]):
    """Delete files of given fragments from disk.
    """
    files = [fragment.path for fragment in fragments]
    if not files:
        return

    f = fsspec.get_mapper(files[0]).fs
    deleted = []
    for file in files:
        f.rm(file)
        deleted.append(file)

    return deleted
