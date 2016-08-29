"""
Computational Cancer Analysis Library v0.1


Authors:
Pablo Tamayo
pablo.tamayo.r@gmail.com
Computational Cancer Analysis, UCSD Cancer Center

Huwate (Kwat) Yeerna (Medetgul-Ernar)
kwat.medetgul.ernar@gmail.com
Computational Cancer Analysis, UCSD Cancer Center

James Jensen
jdjensen@eng.ucsd.edu
Laboratory of Jill Mesirov
"""
import numpy as np
import pandas as pd

# ======================================================================================================================
# Parameters
# ======================================================================================================================
VERBOSE = True
SEED = 20121020


# ======================================================================================================================
# Utilities
# ======================================================================================================================
def print_log(string):
    """
    Print `string` together with logging information.
    :param string: str; message to be printed
    :return: None
    """
    from datetime import datetime

    global VERBOSE
    if VERBOSE:
        print('<{}> {}'.format(datetime.now().strftime('%H:%M:%S'), string))


def install_libraries(libraries_needed):
    """
    Check if `libraries_needed` are installed; if not then install using pip.
    :param libraries_needed: iterable; library names
    :return: None
    """
    from pip import get_installed_distributions, main

    print_log('Checking library dependencies ...')
    libraries_installed = [lib.key for lib in get_installed_distributions()]
    for lib in libraries_needed:
        if lib not in libraries_installed:
            print_log('{} not found! Installing {} using pip ...'.format(lib, lib))
            main(['install', lib])
    print_log('Using the following libraries:')
    for lib in get_installed_distributions():
        if lib.key in libraries_needed:
            print_log('\t{} (v{})'.format(lib.key, lib.version))


def plant_seed(a_seed=SEED):
    """
    Set random seed.
    :param a_seed: int;
    :return: None
    """
    from random import seed
    seed(a_seed)
    print_log('Planted a random seed {}.'.format(SEED))


def establish_path(filepath):
    """
    Make directories up to `fullpath` if they don't already exist.
    :param filepath: str;
    :return: None
    """
    from os import path, mkdir

    if path.isdir(filepath) or path.isfile(filepath) or path.islink(filepath):
        print_log('{} already exists.'.format(filepath))
    else:
        print_log('Full path {} doesn\'t exist, creating it ...'.format(filepath))

        dirs = []
        prefix, suffix = path.split(filepath)
        while suffix != '':
            dirs.append(suffix)
            prefix, suffix = filepath.split(prefix)
        dirs.append(prefix)

        partial_path = ''
        for d in dirs[::-1]:
            partial_path = path.join(partial_path, d)
            if not (path.isdir(partial_path) or path.isfile(partial_path) or path.islink(partial_path)):
                mkdir(partial_path)


def read_gct(filepath, fill_na=None, drop_description=True):
    """
    Read a .gct (`filepath`) and convert it into a pandas DataFrame.
    :param filepath: str;
    :param fill_na: *; value to replace NaN in the DataFrame
    :param drop_description: bool; drop the Description column (column 2 in the .gct) or not
    :return: pandas DataFrame; [n_samples, n_features (or n_features + 1 if not dropping the Description column)]
    """
    df = pd.read_csv(filepath, skiprows=2, sep='\t')
    if fill_na:
        df.fillna(fill_na, inplace=True)
    c1, c2 = df.columns[:2]
    if c1 != 'Name':
        raise ValueError('Column 1 != \'Name\'')
    if c2 != 'Description':
        raise ValueError('Column 2 != \'Description\'')
    df.set_index('Name', inplace=True)
    df.index.name = None
    if drop_description:
        df.drop('Description', axis=1, inplace=True)
    return df


def write_gct(pandas_object, filepath, index_column_name=None, descriptions=None):
    """
    Write a `pandas_object` to a `filepath` as a .gct.
    :param pandas_object: pandas DataFrame or Serires; (n_samples, m_features)
    :param filepath: str;
    :param index_column_name: str; column to be used as the index for the .gct
    :param descriptions: iterable; (n_rows of `pandas_object`), description column for the .gct
    """
    pd_obj = pandas_object.copy()

    # Convert Series to DataFrame
    if isinstance(pd_obj, pd.Series):
        pd_obj = pd.DataFrame(pd_obj).T

    # Set index (Name)
    if index_column_name:
        pd_obj.set_index(index_column_name, inplace=True)
    pd_obj.index.name = 'Name'

    # Set Description
    if descriptions:
        pd_obj.insert(0, 'Description', descriptions)
    else:
        pd_obj.insert(0, 'Description', pd_obj.index)

    # Set output filename suffix
    if not filepath.endswith('.gct'):
        filepath += '.gct'

    with open(filepath, 'w') as f:
        f.writelines('#1.2\n{}\t{}\n'.format(*pd_obj.shape))
        pd_obj.to_csv(f, sep='\t')


# ======================================================================================================================#
# Data analysis functions
# ======================================================================================================================#
def get_unique_in_order(iterable):
    """
    Get unique elements in order.
    :param iterable: iterable;
    :return: list;
    """
    unique_in_order = []
    for x in iterable:
        if x not in unique_in_order:
            unique_in_order.append(x)
    return unique_in_order


def make_random_features(n_row, n_col, n_category=None):
    """
    Make simulation features DataFrame (1D or 2D).
    :param n_row: int, number of rows
    :param n_col: int, number of columns
    :param n_category: None or int, if None, use continuous; if int, use  categorical
    :return: pandas DataFrame, features (`nrow`, `ncol`)
    """
    shape = (n_row, n_col)
    indices = ['Feature {}'.format(i) for i in range(n_row)]
    columns = ['Element {}'.format(i) for i in range(n_col)]
    if n_category:
        features = pd.DataFrame(np.random.random_integers(0, n_category, shape), index=indices, columns=columns)
    else:
        features = pd.DataFrame(np.random.random_sample(shape), index=indices, columns=columns)
    if n_row == 1:
        # Return series
        return features.iloc[0, :]
    else:
        return features


def drop_nan_columns(vectors):
    """
    Keep only column positions that are not nan in all vectors.
    :param vectors: list of numpy array, must have the same length
    :return: list of numpy arrays,
    """
    not_nan_filter = np.ones(len(vectors[0]), dtype=bool)
    for v in vectors:
        not_nan_filter &= ~np.isnan(v)
    return [v[not_nan_filter] for v in vectors]


def add_jitter(vectors, jitter=1E-10):
    """
    Add jitter to vectors.
    :param vectors: numpy array,
    :param jitter: float, jitter
    :return: list of numpy arrays
    """
    return [v + np.random.random_sample(v.size) * jitter for v in vectors]


def normalize_pandas_object(pandas_object, method='-0-'):
    """
    Normalize a pandas object (by row for a DataFrame) using one of various methods.
    :param pandas_object: pandas DataFrame or Series;
    :param method: string; normalization method; {'-0-', '0-1'}
    :return: pandas DataFrame or Series
    """
    obj = pandas_object.copy()
    if method == '-0-':
        if isinstance(obj, pd.DataFrame):
            for i, (idx, s) in enumerate(obj.iterrows()):
                ax_mean = s.mean()
                ax_std = s.std()
                for j, v in enumerate(s):
                    obj.ix[i, j] = (v - ax_mean) / ax_std
        elif isinstance(obj, pd.Series):
            obj = (obj - obj.mean()) / obj.std()
        else:
            raise ValueError('Not a pandas DataFrame or Series.')

    elif method == '0-1':
        if isinstance(obj, pd.DataFrame):
            for i, (idx, s) in enumerate(obj.iterrows()):
                ax_min = s.min()
                ax_max = s.max()
                ax_range = ax_max - ax_min
                for j, v in enumerate(s):
                    obj.ix[i, j] = (v - ax_min) / ax_range
        elif isinstance(obj, pd.Series):
            obj = (obj - obj.min()) / (obj.max() - obj.min())
        else:
            raise ValueError('Not a pandas DataFrame or Series.')
    return obj


def compare_matrices(matrix1, matrix2, function, axis=0, is_distance=False):
    """
    Make association or distance matrix of `matrix1` and `matrix2` by row or column.
    :param matrix1: pandas DataFrame,
    :param matrix2: pandas DataFrame,
    :param function: function, function for computing association or dissociation
    :param axis: int, 0 for by-row and 1 for by-column
    :param is_distance: bool, True for distance and False for association
    :return: pandas DataFrame
    """
    if axis is 1:
        m1 = matrix1.T
        m2 = matrix2.T
    else:
        m1 = matrix1.copy()
        m2 = matrix2.copy()

    compared_matrix = pd.DataFrame(index=m1.index, columns=m2.index, dtype=float)
    nrow = m1.shape[0]
    for i, (i1, r1) in enumerate(m1.iterrows()):
        print_log('Comparing {} ({}/{}) vs. ...'.format(i1, i + 1, nrow))
        for i2, r2 in m2.iterrows():
            compared_matrix.ix[i1, i2] = function(r1, r2)

    if is_distance:
        print_log('Converting association to is_distance (is_distance = 1 - association) ...')
        compared_matrix = 1 - compared_matrix

    return compared_matrix
