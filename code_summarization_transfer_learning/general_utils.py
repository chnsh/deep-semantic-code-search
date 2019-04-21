import logging
import pickle
from itertools import chain
from math import ceil
from pathlib import Path
from typing import List, Callable, Any

import nmslib
import wget
from more_itertools import chunked
from pathos.multiprocessing import Pool, cpu_count


def save_file_pickle(fname: str, obj: Any):
    with open(fname, 'wb') as f:
        pickle.dump(obj, f)


def load_file_pickle(fname: str):
    with open(fname, 'rb') as f:
        obj = pickle.load(f)
        return obj


def read_training_files(data_path: str):
    """
    Read data from directory
    """
    PATH = Path(data_path)

    with open(PATH / 'train.function', 'r', errors='ignore') as f:
        t_enc = f.readlines()

    with open(PATH / 'valid.function', 'r', errors='ignore') as f:
        v_enc = f.readlines()

    # combine train and validation and let keras split it randomly for you
    tv_enc = t_enc + v_enc

    with open(PATH / 'test.function', 'r', errors='ignore') as f:
        h_enc = f.readlines()

    with open(PATH / 'train.docstring', 'r', errors='ignore') as f:
        t_dec = f.readlines()

    with open(PATH / 'valid.docstring', 'r', errors='ignore') as f:
        v_dec = f.readlines()

    # combine train and validation and let keras split it randomly for you
    tv_dec = t_dec + v_dec

    with open(PATH / 'test.docstring', 'r', errors='ignore') as f:
        h_dec = f.readlines()

    with open(PATH / 'train.api_seq', 'r', errors='ignore') as f:
        t_api = f.readlines()

    with open(PATH / 'valid.api_seq', 'r', errors='ignore') as f:
        v_api = f.readlines()

    tv_api = t_api + v_api

    with open(PATH / 'train.function_name', 'r', errors='ignore') as f:
        t_fun = f.readlines()

    with open(PATH / 'valid.function_name', 'r', errors='ignore') as f:
        v_fun = f.readlines()

    tv_fun = t_fun + v_fun

    with open(PATH / 'test.api_seq', 'r', errors='ignore') as f:
        h_api = f.readlines()

    with open(PATH / 'test.function_name', 'r', errors='ignore') as f:
        h_fun = f.readlines()

    logging.warning(f'Num rows for encoder training + validation input: {len(tv_enc):,}')
    logging.warning(f'Num rows for encoder holdout input: {len(h_enc):,}')

    logging.warning(f'Num rows for decoder training + validation input: {len(tv_dec):,}')
    logging.warning(f'Num rows for decoder holdout input: {len(h_dec):,}')

    logging.warning(f'Num rows for encoder training + validation input: {len(tv_api):,}')
    logging.warning(f'Num rows for encoder holdout input: {len(h_api):,}')

    logging.warning(f'Num rows for decoder training + validation input: {len(tv_fun):,}')
    logging.warning(f'Num rows for decoder holdout input: {len(h_fun):,}')

    return tv_enc, h_enc, tv_dec, h_dec, tv_api, h_api, tv_fun, h_fun


def apply_parallel(func: Callable,
                   data: List[Any],
                   cpu_cores: int = None) -> List[Any]:
    """
    Apply function to list of elements.
    Automatically determines the chunk size.
    """
    if not cpu_cores:
        cpu_cores = cpu_count()

    try:
        chunk_size = ceil(len(data) / cpu_cores)
        pool = Pool(cpu_cores)
        transformed_data = pool.map(func, chunked(data, chunk_size), chunksize=1)
    finally:
        pool.close()
        pool.join()
        return transformed_data


def flattenlist(listoflists: List[List[Any]]):
    return list(chain.from_iterable(listoflists))


processed_data_filenames = [
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/test.docstring',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/test.function',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/test.lineage',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/test_original_function.json.gz',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/train.docstring',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/train.function',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/train.lineage',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/train_original_function.json.gz',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/valid.docstring',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/valid.function',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/valid.lineage',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/valid_original_function.json.gz',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/without_docstrings.function',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/without_docstrings.lineage',
    'https://storage.googleapis.com/kubeflow-examples/code_search/data/without_docstrings_original_function.json.gz']


def get_step2_prerequisite_files(output_directory):
    outpath = Path(output_directory)
    assert not list(outpath.glob('*')), f'There are files in {str(outpath.absolute())},' \
        f' please clear files or specify an empty folder.'
    outpath.mkdir(exist_ok=True)
    print(f'Saving files to {str(outpath.absolute())}')
    for url in processed_data_filenames:
        print(f'downloading {url}')
        wget.download(url, out=str(outpath.absolute()))


def create_nmslib_search_index(numpy_vectors):
    """Create search index using nmslib.

    Parameters
    ==========
    numpy_vectors : numpy.array
        The matrix of vectors

    Returns
    =======
    nmslib object that has index of numpy_vectors
    """

    search_index = nmslib.init(method='hnsw', space='cosinesimil')
    search_index.addDataPointBatch(numpy_vectors)
    search_index.createIndex({'post': 2}, print_progress=True)
    return search_index
