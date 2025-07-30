# Copyright 2025 TOYOTA MOTOR CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations
from typing import TypeVar, Any, Sequence
import json
import itertools

import pandas as _pd

from .. import egrpc
from ..util import DPError
from ..prisoner import SensitiveInt
from ..distance import Distance
from .util import ElementType, PrivPandasExclusiveDummy, assert_ptag
from .domain import CategoryDomain, normalize_column_schema, apply_column_schema, column_schema2domain
from .series import PrivSeries
from .dataframe import PrivDataFrame, SensitiveDataFrame

T = TypeVar("T")

@egrpc.function
def read_csv(filepath: str, schemapath: str | None = None) -> PrivDataFrame:
    # TODO: more vaildation for the input data
    df = _pd.read_csv(filepath)

    if schemapath is not None:
        with open(schemapath, "r") as f:
            schema = json.load(f)
    else:
        schema = dict()

    domains = dict()
    for col in df.columns:
        if not isinstance(col, str):
            raise ValueError("Column name must be a string.")

        if col in schema:
            col_schema = schema[col]
        else:
            col_schema = dict(type="string" if df.dtypes[col] == "object" else df.dtypes[col])

        col_schema = normalize_column_schema(col_schema)

        df[col] = apply_column_schema(df[col], col_schema, col)

        domains[col] = column_schema2domain(col_schema)

    return PrivDataFrame(data=df, domains=domains, distance=Distance(1), root_name=filepath)

def crosstab(index        : PrivSeries[ElementType], # TODO: support Sequence[PrivSeries[ElementType]]
             columns      : PrivSeries[ElementType], # TODO: support Sequence[PrivSeries[ElementType]]
             values       : PrivSeries[ElementType] | None = None,
             rownames     : list[str] | None               = None,
             colnames     : list[str] | None               = None,
             rowvalues    : Sequence[ElementType] | None   = None, # extra argument for privjail
             colvalues    : Sequence[ElementType] | None   = None, # extra argument for privjail
             *,
             aggfunc      : None                           = None,
             margins      : bool                           = False,
             margins_name : str                            = "All",
             dropna       : bool                           = True,
             normalize    : bool | str | int               = False, # TODO: support Literal["all", "index", "columns", 0, 1] in egrpc
             ) -> SensitiveDataFrame:
    result = _crosstab_impl(index, columns, values, rownames, colnames, rowvalues, colvalues,
                            aggfunc=aggfunc, margins=margins, margins_name=margins_name,
                            dropna=dropna, normalize=normalize)

    rowvalues, colvalues, data = result
    priv_counts = SensitiveDataFrame(index=rowvalues, columns=colvalues)

    for i, (idx, col) in enumerate(itertools.product(rowvalues, colvalues)):
        priv_counts.loc[idx, col] = data[i] # type: ignore

    return priv_counts

@egrpc.function
def _crosstab_impl(index        : PrivSeries[ElementType], # TODO: support Sequence[PrivSeries[ElementType]]
                   columns      : PrivSeries[ElementType], # TODO: support Sequence[PrivSeries[ElementType]]
                   values       : PrivSeries[ElementType] | None = None,
                   rownames     : list[str] | None               = None,
                   colnames     : list[str] | None               = None,
                   rowvalues    : Sequence[ElementType] | None   = None, # extra argument for privjail
                   colvalues    : Sequence[ElementType] | None   = None, # extra argument for privjail
                   *,
                   aggfunc      : None                           = None,
                   margins      : bool                           = False,
                   margins_name : str                            = "All",
                   dropna       : bool                           = True,
                   normalize    : bool | str | int               = False, # TODO: support Literal["all", "index", "columns", 0, 1] in egrpc
                   ) -> tuple[list[ElementType], list[ElementType], list[SensitiveInt]]:
    if normalize is not False:
        # TODO: what is the sensitivity?
        print(normalize)
        raise NotImplementedError

    if values is not None or aggfunc is not None:
        # TODO: hard to accept arbitrary user functions
        raise NotImplementedError

    if margins:
        # Sensitivity must be managed separately for value counts and margins
        raise DPError("`margins=True` is not supported. Please manually calculate margins after adding noise.")

    if isinstance(index.domain, CategoryDomain):
        rowvalues = index.domain.categories

    if rowvalues is None:
        raise DPError("Please specify `rowvalues` to prevent privacy leakage.")

    if isinstance(columns.domain, CategoryDomain):
        colvalues = columns.domain.categories

    if colvalues is None:
        raise DPError("Please specify `colvalues` to prevent privacy leakage.")

    # if not dropna and (not any(_np.isnan(rowvalues)) or not any(_np.isnan(colvalues))):
    #     # TODO: consider handling for pd.NA
    #     warnings.warn("Counts for NaN will be dropped from the result because NaN is not included in `rowvalues`/`colvalues`", UserWarning)

    assert_ptag(index, columns)

    counts = _pd.crosstab(index._value, columns._value,
                          values=None, rownames=rownames, colnames=colnames,
                          aggfunc=None, margins=False, margins_name=margins_name,
                          dropna=dropna, normalize=False)

    # Select only the specified values and fill non-existent counts with 0
    counts = counts.reindex(list(rowvalues), axis="index") \
                   .reindex(list(colvalues), axis="columns") \
                   .fillna(0).astype(int)

    distances = index.distance.create_exclusive_distances(counts.size)

    prisoner_dummy = PrivPandasExclusiveDummy(parents=[index, columns])

    data = [SensitiveInt(counts.loc[idx, col], distance=distances[i], parents=[prisoner_dummy]) # type: ignore
            for i, (idx, col) in enumerate(itertools.product(rowvalues, colvalues))]

    return list(rowvalues), list(colvalues), data

# TODO: change multifunction -> function by type checking in egrpc.function
@egrpc.multifunction
def cut(x              : PrivSeries[Any],
        bins           : list[int] | list[float],
        right          : bool                            = True,
        labels         : list[ElementType] | bool | None = None,
        retbins        : bool                            = False,
        precision      : int                             = 3,
        include_lowest : bool                            = False
        # TODO: add more parameters
        ) -> PrivSeries[Any]:
    ser = _pd.cut(x._value, bins=bins, right=right, labels=labels, retbins=retbins, precision=precision, include_lowest=include_lowest) # type: ignore

    new_domain = CategoryDomain(categories=list(ser.dtype.categories))

    return PrivSeries[Any](ser, domain=new_domain, distance=x.distance, parents=[x], preserve_row=True)
