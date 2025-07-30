from functools import reduce

import pandas as pd
from tqdm.auto import tqdm


def flatten_column_index(column_index, skip_first_second=False):
    """
    Flatten a MultiIndex column index to a single-level list of column names.

    Args:
        column_index (pd.MultiIndex): The MultiIndex of a DataFrame's columns.
        skip_first_second (bool): If True, skip adding the second-level name
                                  for the first column in each multi-column group.

    Returns:
        List[str]: A list of flattened column names.

        Example:
        >>> import pandas as pd
        >>> cols = pd.MultiIndex.from_tuples([
        ...     ('user', ''),
        ...     ('score', 'mean'),
        ...     ('score', 'std'),
        ...     ('comment', '')
        ... ])
        >>> flatten_column_index(cols, skip_first_second=False)
        ['user', 'score_mean', 'score_std', 'comment']

        >>> flatten_column_index(cols, skip_first_second=True)
        ['user', 'score', 'score_std', 'comment']
    """
    new_columns = []
    for first_level in column_index.get_level_values(0).unique():
        second_level = column_index[column_index.get_level_values(0) == first_level].get_level_values(1)
        if len(second_level) == 1:
            new_columns.append(first_level)
        else:
            for i, second in enumerate(second_level):
                if skip_first_second and i == 0:
                    new_columns.append(first_level)
                else:
                    new_columns.append(f'{first_level}_{second}')
    return new_columns


def panelize(data, i, t, agg, fillna=None, rename=None, trange=None):
    if fillna is None:
        fillna = {}
    if rename is None:
        rename = {}

    def union(series):
        return reduce(set.union,
                      [(set(r.split('|')) if r else set()) if isinstance(r, str) else r for r in series])

    def replace_agg(v):
        if isinstance(v, list):
            return [replace_agg(vv) for vv in v]
        if v in {'union', 'nuniques'}:
            v = union
        return v

    def fillgap(df):
        df = df.sort_values(by=t).set_index(t)
        if trange is not None:
            left, right = trange
            if left is None: left = df.index.min()
            if right is None: right = df.index.max() + 1
            df = df.reindex(pd.RangeIndex(left, right, name=t)).reset_index(t)
            df[i] = df[i].ffill().bfill()  #.fillna(method='ffill').fillna(method='bfill')
            df = df.fillna({k: fillna.get(k, 0) if v not in {'union', 'nuniques'} else '' for k, v in agg.items()})
        else:
            for k, v in agg.items():
                if v in {'union', 'nuniques'}:
                    df[k] = df[k].fillna('')
        # for k, v in agg.items():
        #     df[k] = df[k].fillna(fillna.get(k, 0) if v not in {'union', 'nuniques'} else '')
        return df

    tqdm.pandas()
    data = data.groupby([i, t], as_index=False).agg({k: replace_agg(v) for k, v in agg.items()})
    if trange is not None:
        data = data.groupby(i, as_index=False).progress_apply(fillgap)
    for k, v in agg.items():
        # if v == 'union':
        #     data[f'{rename.get(k, k)}_nunique'] = data[k].apply(len)
        if v == 'nuniques':
            data[k] = data[k].apply(len)

    if rename:
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = pd.MultiIndex.from_tuples([
                (rename.get(col[0], col[0]), *col[1:]) if len(col) > 1 else (rename.get(col[0], col[0]),)
                for col in data.columns.to_list()
            ])
        else:
            return data.rename(columns=rename)
    return data
