import datetime
import os
from copy import deepcopy
from functools import wraps
from typing import Literal

import numpy as np
import pandas as pd

import els.config as ec
import els.core as el
from els._typing import listify

from . import helpers as th

inflight: dict[str, pd.DataFrame] = {}


def get_flight_url(test_medium):
    if test_medium == "pandas":
        return el.urlize_dict(inflight)
    elif test_medium == "csv":
        return "*.csv"
    elif test_medium == "excel":
        return th.filename_from_dir("xlsx")
    elif test_medium == "sqlite":
        return f"sqlite:///{th.filename_from_dir('db')}"
    elif test_medium == "duckdb":
        return f"duckdb:///{th.filename_from_dir('db')}"
    elif test_medium == "mssql":
        db_host = os.getenv("TEST_ELS_MSSQL_HOST", "localhost")
        dbname = os.environ.get("PYTEST_CURRENT_TEST").split(" ")[0].split("[")[-1][:-1]
        test_url = f"mssql://sa:dbatools.I0@{db_host}/{dbname}"
        return test_url
    elif test_medium == "xml":
        return "*.xml"


def configify(config, test_medium, pp: Literal["push", "pull"]):
    for i, c in enumerate(listify(config)):
        if isinstance(c, ec.Target):
            cc = ec.Config(target=c)
        elif isinstance(c, ec.Source):
            cc = ec.Config(source=c)
        else:
            cc = c
        # if pp == "pull":
        #     cc.source.url = flight_url()
        if pp == "push":
            cc.target.url = get_flight_url(test_medium)
        if i == 0 and cc.target.type == "mssql":
            cc.target.if_exists = "replace_database"
        yield cc


def oneway_config(test_medium, config_for, outbound, expected, config):
    inflight.clear()
    if config_for == "push":
        for cc in configify(config, test_medium=test_medium, pp="push"):
            push(test_medium=test_medium, config=cc, outbound=outbound)
        inbound = pull(test_medium=test_medium)
    elif config_for == "pull":
        pull_config = ec.Config(target=ec.Target(url=get_flight_url(test_medium)))
        if pull_config.target.type == "mssql":
            pull_config.target.if_exists = "replace_database"
        push(test_medium=test_medium, outbound=outbound, config=pull_config)
        inbound = {}
        for cc in configify(config, test_medium=test_medium, pp="pull"):
            inbound = pull(test_medium=test_medium, config=cc, inbound=inbound)
    else:
        assert False
    th.assert_expected(expected, actual=inbound)


def twoway_config(test_medium, outbound, expected, config_push, config_pull):
    inflight.clear()
    for cc in configify(config_push, test_medium=test_medium, pp="push"):
        push(test_medium=test_medium, config=cc, outbound=outbound)
    inbound = {}
    for cc in configify(config_pull, test_medium=test_medium, pp="pull"):
        inbound = pull(test_medium=test_medium, config=cc, inbound=inbound)
    th.assert_expected(expected, actual=inbound)


def config_push_pull(func):
    @wraps(func)
    def wrapper(test_medium):
        outbound, expected, config_push, config_pull = func()
        twoway_config(test_medium, outbound, expected, config_push, config_pull)

    return wrapper


@config_push_pull
def skiprows_csv1():
    outbound = dict(
        df=pd.DataFrame(
            {
                "no header in this export": [
                    np.nan,
                    np.nan,
                    "a",
                    "b",
                    "c",
                    "d",
                ]
            }
        )
    )
    expected = dict(
        df=pd.DataFrame(
            {
                "Unnamed: 0": [
                    np.nan,
                    "a",
                    "b",
                    "c",
                    "d",
                ]
            }
        )
    )
    config_push = ec.Config(target=ec.Target(write_args=ec.ToCSV(header=False)))
    config_pull = ec.Config()
    return outbound, expected, config_push, config_pull


@config_push_pull
def skiprows_csv2():
    outbound = dict(
        df=pd.DataFrame(
            {
                "no header in this export": [
                    np.nan,
                    np.nan,
                    "a",
                    "b",
                    "c",
                    "d",
                ]
            }
        )
    )
    expected = dict(
        df=pd.DataFrame(
            {
                "a": [
                    "b",
                    "c",
                    "d",
                ]
            }
        )
    )
    config_push = ec.Config(
        target=ec.Target(
            write_args=ec.ToCSV(header=False),
        )
    )
    config_pull = ec.Config(
        source=ec.Source(
            read_args=ec.ReadCSV(skiprows=2),
        )
    )
    return outbound, expected, config_push, config_pull


@config_push_pull
def skiprows_csv3():
    outbound = dict(
        df=pd.DataFrame(
            {
                "no header in this export": [
                    np.nan,
                    np.nan,
                    "a",
                    "b",
                    "c",
                    "d",
                ]
            }
        )
    )
    expected = dict(
        df=pd.DataFrame(
            {
                "a": [
                    "b",
                    "c",
                    "d",
                ]
            }
        )
    )
    expected["df"]["_header"] = str([[""], [""]])
    config_push = ec.Config(
        target=ec.Target(
            write_args=ec.ToCSV(header=False),
        )
    )
    config_pull = ec.Config(
        source=ec.Source(
            read_args=ec.ReadCSV(
                skiprows=2,
                capture_header=True,
            ),
        )
    )
    return outbound, expected, config_push, config_pull


@config_push_pull
def skipfoot_csv1():
    outbound = dict(df=pd.DataFrame({"a": [1, 2, 3, None, None, "footer"]}))
    expected = dict(df=pd.DataFrame({"a": [1, 2, 3]}))
    config_push = ec.Config()
    config_pull = ec.Config(source=ec.Source(read_args=ec.ReadCSV(skipfooter=3)))
    return outbound, expected, config_push, config_pull


@config_push_pull
def skipfoot_csv2():
    outbound = dict(df=pd.DataFrame({"a": [1, 2, 3, None, None, "footer"]}))
    expected = dict(df=pd.DataFrame({"a": [1, 2, 3]}))
    expected["df"]["_footer"] = str([[""], [""], ["footer"]])
    config_push = ec.Config()
    config_pull = ec.Config(
        source=ec.Source(
            read_args=ec.ReadCSV(
                skipfooter=3,
                capture_footer=True,
            )
        )
    )
    return outbound, expected, config_push, config_pull


@config_push_pull
def skiprows_xl1():
    outbound = dict(df=pd.DataFrame({"a": [1, 2, 3]}))
    expected = dict(df=pd.DataFrame({"Unnamed: 0": [np.nan, "a", 1, 2, 3]}))
    config_push = ec.Config(
        target=ec.Target(
            write_args=ec.ToExcel(startrow=2),
        )
    )

    config_pull = ec.Config()
    return outbound, expected, config_push, config_pull


@config_push_pull
def skiprows_xl2():
    outbound = dict(df=pd.DataFrame({"a": [1, 2, 3]}))
    expected = outbound.copy()
    config_push = ec.Config(
        target=ec.Target(
            write_args=ec.ToExcel(startrow=2),
        )
    )
    config_pull = ec.Config(
        source=ec.Source(
            read_args=ec.ReadExcel(skiprows=2),
        )
    )
    return outbound, expected, config_push, config_pull


@config_push_pull
def skiprows_xl3():
    outbound = dict(df=pd.DataFrame({"a": [1, 2, 3]}))
    expected = deepcopy(outbound)
    expected["df"]["_header"] = str([[""], [""]])
    config_push = ec.Config(
        target=ec.Target(
            write_args=ec.ToExcel(startrow=2),
        )
    )
    config_pull = ec.Config(
        source=ec.Source(
            read_args=ec.ReadExcel(
                skiprows=2,
                capture_header=True,
            ),
        )
    )
    return outbound, expected, config_push, config_pull


@config_push_pull
def skipfoot_xl1():
    outbound = dict(df=pd.DataFrame({"a": [1, 2, 3, None, None, "footer"]}))
    expected = dict(df=pd.DataFrame({"a": [1, 2, 3]}))
    config_push = ec.Config()
    config_pull = ec.Config(source=ec.Source(read_args=ec.ReadExcel(skipfooter=3)))
    return outbound, expected, config_push, config_pull


@config_push_pull
def skipfoot_xl2():
    outbound = dict(df=pd.DataFrame({"a": [1, 2, 3, None, None, "footer"]}))
    expected = dict(df=pd.DataFrame({"a": [1, 2, 3]}))
    expected["df"]["_footer"] = str([[""], [""], ["footer"]])
    config_push = ec.Config()
    config_pull = ec.Config(
        source=ec.Source(
            read_args=ec.ReadExcel(
                skipfooter=3,
                capture_footer=True,
            )
        )
    )
    return outbound, expected, config_push, config_pull


def config_symmetrical(func):
    @wraps(func)
    def wrapper(test_medium, config_for):
        outbound, expected, config = func()
        oneway_config(test_medium, config_for, outbound, expected, config)

    return wrapper


def config_pull(func):
    @wraps(func)
    def wrapper(test_medium):
        outbound, expected, config = func()
        oneway_config(test_medium, "pull", outbound, expected, config)

    return wrapper


def config_push(func):
    @wraps(func)
    def wrapper(test_medium):
        outbound, expected, config = func()
        oneway_config(test_medium, "push", outbound, expected, config)

    return wrapper


@config_symmetrical
def single():
    outbound = dict(
        df_single=pd.DataFrame({"a": [1, 2, 3]}),
    )
    expected = outbound
    config = ec.Config()
    return outbound, expected, config


@config_symmetrical
def double_together():
    outbound = dict(
        dfa=pd.DataFrame({"a": [1, 2, 3]}),
        dfb=pd.DataFrame({"b": [4, 5, 6]}),
    )
    expected = outbound
    config = ec.Config()
    return outbound, expected, config


@config_symmetrical
def double_separate():
    outbound = dict(
        dfa=pd.DataFrame({"a": [1, 2, 3]}),
        dfb=pd.DataFrame({"b": [4, 5, 6]}),
    )
    expected = outbound
    config = [
        ec.Source(table="dfa"),
        ec.Source(table="dfb"),
    ]
    return (
        outbound,
        expected,
        config,
    )


@config_symmetrical
def double_together2():
    outbound = dict(
        dfa=pd.DataFrame({"a": [1, 2, 3]}),
        dfb=pd.DataFrame({"b": [4, 5, 6]}),
    )
    expected = dict(
        dfa=pd.DataFrame({"a": [1, 2, 3]}),
    )
    config = ec.Source(table="dfa")
    return outbound, expected, config


@config_symmetrical
def append_together():
    outbound = dict(
        dfa=pd.DataFrame({"a": [1, 2, 3]}),
        dfb=pd.DataFrame({"a": [10, 20, 30]}),
    )
    expected = dict(
        df=pd.DataFrame({"a": [1, 2, 3, 10, 20, 30]}),
    )
    config = ec.Target(table="df")
    return outbound, expected, config


@config_symmetrical
def append_separate():
    outbound = dict(
        dfa=pd.DataFrame({"a": [1, 2, 3]}),
        dfb=pd.DataFrame({"a": [10, 20, 30]}),
    )
    expected = dict(
        df=pd.DataFrame({"a": [1, 2, 3, 10, 20, 30]}),
    )
    config = [
        ec.Config(
            source=ec.Source(table="dfa"),
            target=ec.Target(table="df"),
        ),
        ec.Config(
            source=ec.Source(table="dfb"),
            target=ec.Target(table="df", if_exists="append"),
        ),
    ]
    return outbound, expected, config


@config_symmetrical
def append_mixed():
    outbound = dict(
        dfa=pd.DataFrame(
            {
                "a": [1, 2, 3],
                "b": [4, 5, 6],
            }
        ),
        dfb=pd.DataFrame(
            {
                "b": [40, 50, 60],
                "a": [10, 20, 30],
            }
        ),
    )
    expected = dict(
        df=pd.DataFrame(
            {
                "a": [1, 2, 3, 10, 20, 30],
                "b": [4, 5, 6, 40, 50, 60],
            }
        )
    )
    config = ec.Target(table="df", if_exists="append")
    return outbound, expected, config


@config_symmetrical
def append_plus():
    outbound = dict(
        dfa=pd.DataFrame(
            {
                "a": [1, 2, 3],
                "b": [4, 5, 6],
            }
        ),
        dfb=pd.DataFrame(
            {
                "b": [40, 50, 60],
                "a": [10, 20, 30],
                "c": [70, 80, 90],
            }
        ),
    )
    expected = dict(
        df=pd.DataFrame(
            {
                "a": [1, 2, 3, 10, 20, 30],
                "b": [4, 5, 6, 40, 50, 60],
            }
        )
    )
    config = ec.Target(table="df", if_exists="append", consistency="ignore")
    return outbound, expected, config


@config_symmetrical
def append_minus():
    # adding Nones to coerce datatypes to floats
    outbound = dict(
        dfa=pd.DataFrame(
            {
                "a": [1, 2, None, 3],
                "b": [4, 5, None, 6],
            }
        ),
        dfb=pd.DataFrame(
            {
                "b": [40, 50, 60],
            }
        ),
    )
    expected = dict(
        df=pd.DataFrame(
            {
                "a": [1, 2, None, 3, None, None, None],
                "b": [4, 5, None, 6, 40, 50, 60],
            }
        )
    )
    config = ec.Target(table="df", if_exists="append", consistency="ignore")
    return outbound, expected, config


@config_symmetrical
def truncate_single():
    outbound = dict(
        dfa=pd.DataFrame(
            {
                "a": [1, 2, 3],
                "b": [4, 5, 6],
            }
        ),
        dfb=pd.DataFrame(
            {
                "b": [30],
                "a": [10],
                "c": [50],
            }
        ),
    )
    expected = dict(
        df=pd.DataFrame(
            {
                "a": [10],
                "b": [30],
            }
        )
    )
    config = [
        ec.Config(
            source=ec.Source(table="dfa"),
            target=ec.Target(table="df"),
        ),
        ec.Config(
            source=ec.Source(table="dfb"),
            target=ec.Target(table="df", if_exists="truncate", consistency="ignore"),
        ),
    ]
    return outbound, expected, config


@config_symmetrical
def truncate_double():
    outbound = dict(
        df=pd.DataFrame(
            {
                "a": [1, 2, 3],
                "b": [4, 5, 6],
            }
        ),
        dfa=pd.DataFrame(
            {
                "b": [50, 60],
                "a": [10, 20],
            }
        ),
        dfb=pd.DataFrame(
            {
                "b": [70, 80],
            }
        ),
    )
    expected = dict(
        df=pd.DataFrame(
            {
                "a": [10, 20, None, None],
                "b": [50, 60, 70, 80],
            }
        )
    )
    config = [
        ec.Source(table="df"),
        ec.Config(
            source=ec.Source(table=["dfa", "dfb"]),
            target=ec.Target(if_exists="truncate", consistency="ignore", table="df"),
        ),
    ]
    return outbound, expected, config


@config_symmetrical
def replace():
    outbound = dict(
        dfa=pd.DataFrame({"a": [1, 2, 3]}),
        dfb=pd.DataFrame({"b": [4, 5, 6]}),
        dfbb=pd.DataFrame({"bb": [44, 55, 66]}),
    )
    expected = dict(
        dfa=pd.DataFrame({"a": [1, 2, 3]}),
        dfb=pd.DataFrame({"bb": [44, 55, 66]}),
    )
    config = [
        ec.Source(table=["dfa", "dfb"]),
        ec.Config(
            source=ec.Source(table="dfbb"),
            target=ec.Target(table="dfb", if_exists="replace"),
        ),
    ]
    return outbound, expected, config


# TODO: split_on_column_implicit_table


@config_symmetrical
def split_on_col_explicit_tab():
    outbound = dict(
        dfo=pd.DataFrame(
            {
                "split_col": ["t1", "t1", "t2", "t2"],
                "a": [1, 2, 3, 4],
                "b": [10, 20, 30, 40],
            }
        )
    )
    expected = dict(
        t1=pd.DataFrame(
            {
                "split_col": ["t1", "t1"],
                "a": [1, 2],
                "b": [10, 20],
            }
        ),
        t2=pd.DataFrame(
            {
                "split_col": ["t2", "t2"],
                "a": [3, 4],
                "b": [30, 40],
            }
        ),
    )
    config = ec.Config(
        source=ec.Source(table="dfo"),
        transforms=[ec.SplitOnColumn(split_on_column="split_col")],
        # transform=ec.SplitOnColumn(split_on_column="split_col"),
        # transforms=[
        #     ec.Transform_(split_on_column=ec.SplitOnColumn(split_on_column="split_col"))
        # ],
    )
    return outbound, expected, config


@config_symmetrical
def prql_split():
    outbound = dict(
        dfo=pd.DataFrame(
            {
                "split_col": ["t1", "t1", "t2", "t2", "t3", "t3"],
                "a": [1, 2, 3, 4, 5, 6],
                "b": [10, 20, 30, 40, 50, 60],
            }
        )
    )
    expected = dict(
        t1=pd.DataFrame(
            {
                "split_col": ["t1", "t1"],
                "a": [1, 2],
                "b": [10, 20],
            }
        ),
        t2=pd.DataFrame(
            {
                "split_col": ["t2", "t2"],
                "a": [3, 4],
                "b": [30, 40],
            }
        ),
    )
    config = ec.Config(
        source=ec.Source(table="dfo"),
        transforms=[
            ec.PRQLTransform(
                prql="""
            from df
            filter a < 5
            """
            ),
            ec.SplitOnColumn(split_on_column="split_col"),
        ],
    )
    return outbound, expected, config


@config_symmetrical
def prql():
    outbound = dict(
        dfo=pd.DataFrame(
            {
                "a": [1, 2, 3, 4],
                "b": [10, 20, 30, 40],
            }
        )
    )
    expected = dict(
        dfo=pd.DataFrame(
            {
                "a": [1, 2],
                "b": [10, 20],
            }
        )
    )
    config = ec.Config(
        source=ec.Source(table="dfo"),
        transforms=[
            ec.PRQLTransform(
                prql="""
            from df
            filter a < 3
            """
            )
        ],
    )
    return outbound, expected, config


@config_symmetrical
def filter():
    outbound = dict(
        dfo=pd.DataFrame(
            {
                "a": [1, 2, 3, 4],
                "b": [10, 20, 30, 40],
            }
        )
    )
    expected = dict(
        dfo=pd.DataFrame(
            {
                "a": [1, 2],
                "b": [10, 20],
            }
        )
    )
    config = ec.Config(
        source=ec.Source(table="dfo"),
        transforms=[ec.FilterTransform(filter="a < 3")],
    )
    return outbound, expected, config


@config_symmetrical
def pivot():
    outbound = dict(
        dfo=pd.DataFrame(
            {
                "split_col": ["t1", "t1", "t2", "t2", "t3", "t3"],
                "a": [1, 2, 1, 2, 1, 2],
                "b": ["a", "b", "c", "d", "e", "f"],
            }
        )
    )
    expected = dict(
        dfo=pd.DataFrame(
            {
                "t1": ["a", "b"],
                "t2": ["c", "d"],
                "t3": ["e", "f"],
            }
        )
    )
    config = ec.Config(
        source=ec.Source(table="dfo"),
        transforms=[
            ec.Pivot(pivot_columns="split_col", pivot_values="b", pivot_index="a")
        ],
    )
    return outbound, expected, config


@config_symmetrical
def prql_split_pivot():
    outbound = dict(
        dfo=pd.DataFrame(
            {
                "split_col": ["t1", "t1", "t2", "t2", "t3", "t3"],
                "a": [1, 2, 1, 2, 1, 2],
                "b": [10, 20, 30, 40, 50, 60],
            }
        )
    )
    expected = dict(
        t1=pd.DataFrame({"t1": [10, 20]}),
        t2=pd.DataFrame({"t2": [30, 40]}),
    )
    config = ec.Config(
        source=ec.Source(table="dfo"),
        transforms=[
            ec.PRQLTransform(
                prql="""
            from df
            filter b < 50
            """
            ),
            ec.SplitOnColumn(
                split_on_column="split_col",
            ),
            ec.Pivot(
                pivot_columns="split_col",
                pivot_values="b",
                pivot_index="a",
            ),
        ],
    )
    return outbound, expected, config


@config_symmetrical
def prql_col_split_pivot():
    outbound = dict(
        dfo=pd.DataFrame(
            {
                "split_col": ["t1", "t1", "t2", "t2", "t3", "t3"],
                "a": [1, 2, 1, 2, 1, 2],
                "b": [10, 20, 30, 40, 50, 60],
            }
        )
    )
    expected = dict(
        t1_2=pd.DataFrame({"t1": [10, 20]}),
        t2_2=pd.DataFrame({"t2": [30, 40]}),
    )
    config = ec.Config(
        source=ec.Source(table="dfo"),
        transforms=[
            ec.PRQLTransform(
                prql="""
            from df
            filter b < 50
            derive {new_split = f"{split_col}_2"}
            """
            ),
            ec.SplitOnColumn(
                split_on_column="new_split",
            ),
            ec.Pivot(
                pivot_columns="split_col",
                pivot_values="b",
                pivot_index="a",
            ),
        ],
    )
    return outbound, expected, config


@config_symmetrical
def prql_col_split():
    outbound = dict(
        dfo=pd.DataFrame(
            {
                "split_col": ["t1", "t1", "t2", "t2", "t3", "t3"],
                "a": [1, 2, 1, 2, 1, 2],
                "b": [10, 20, 30, 40, 50, 60],
            }
        )
    )
    expected = dict(
        t1_2=pd.DataFrame(
            {
                "split_col": ["t1", "t1"],
                "a": [1, 2],
                "b": [10, 20],
                "new_split": ["t1_2", "t1_2"],
            }
        ),
        t2_2=pd.DataFrame(
            {
                "split_col": ["t2", "t2"],
                "a": [1, 2],
                "b": [30, 40],
                "new_split": ["t2_2", "t2_2"],
            }
        ),
    )
    config = ec.Config(
        source=ec.Source(table="dfo"),
        transforms=[
            ec.PRQLTransform(
                prql="""
            from df
            filter b < 50
            derive {new_split = f"{split_col}_2"}
            """
            ),
            ec.SplitOnColumn(
                split_on_column="new_split",
            ),
        ],
    )
    return outbound, expected, config


@config_pull
def astype():
    outbound = dict(
        dfo=pd.DataFrame(
            {
                "a": [1, 2],
                "b": [10, 20],
            }
        )
    )
    expected = dict(
        dfo=pd.DataFrame(
            {
                "a": [1.0, 2.0],
                "b": [10, 20],
            }
        )
    )
    config = ec.Config(
        source=ec.Source(table="dfo"),
        transforms=[ec.AsType(as_dtypes=dict(a="float"))],
    )
    return outbound, expected, config


@config_symmetrical
def melt():
    outbound = dict(
        dfo=pd.DataFrame(
            {
                "A": ["a", "b", "c"],
                "B": [1, 3, 5],
                "C": [2, 4, 6],
            }
        )
    )
    expected = dict(
        dfo=pd.DataFrame(
            {
                "A": ["a", "b", "c"],
                "col": ["B", "B", "B"],
                "val": [1, 3, 5],
            }
        )
    )
    config = ec.Config(
        source=ec.Source(table="dfo"),
        transforms=[
            ec.Melt(
                melt_id_vars=["A"],
                melt_value_vars=["B"],
                melt_var_name="col",
                melt_value_name="val",
            )
        ],
    )
    return outbound, expected, config


@config_push
def stack_dynamic():
    outbound = dict(
        dfo=pd.DataFrame(
            columns=pd.MultiIndex.from_tuples(
                [
                    ("Fixed1", None),
                    ("Fixed2", None),
                    ("Group A", "One"),
                    ("Group A", "Two"),
                    ("Group B", "One"),
                    ("Group B", "Two"),
                ]
            ),
            data=[[1, 2, 3, 4, 5, 6]],
        )
    )
    expected = dict(
        dfo=pd.DataFrame(
            {
                "Fixed1": [1, 1],
                "Fixed2": [2, 2],
                "col": ["Group A", "Group B"],
                "One": [3, 5],
                "Two": [4, 6],
            }
        )
    )
    config = ec.Config(
        source=ec.Source(table="dfo"),
        transforms=[ec.StackDynamic(stack_fixed_columns=2, stack_name="col")],
    )
    return outbound, expected, config


@config_symmetrical
def add_columns():
    outbound = dict(
        dfo=pd.DataFrame(
            {
                "a": [1, 2],
                "b": [10, 20],
            }
        )
    )
    expected = dict(
        dfo=pd.DataFrame(
            {
                "a": [1, 2],
                "b": [10, 20],
                "test": [100, 100],
            }
        )
    )
    config = ec.Config(
        source=ec.Source(table="dfo"),
        transforms=[ec.AddColumns(test=100)],
    )
    return outbound, expected, config


@config_push
def replace_file():
    outbound = dict(
        df1=pd.DataFrame({"a": [1, 2, 3]}), df2=pd.DataFrame({"b": [4, 5, 6]})
    )
    expected = dict(df2=pd.DataFrame({"b": [4, 5, 6]}))

    config = [
        ec.Config(),
        ec.Config(
            source=ec.Source(table="df2"),
            target=ec.Target(if_exists="replace_file"),
        ),
    ]
    return outbound, expected, config


@config_push
def multiindex_column():
    outbound = dict(
        dfx=pd.DataFrame(
            columns=pd.MultiIndex.from_product([["A", "B"], ["c", "d", "e"]]),
            data=[[1, 2, 3, 4, 5, 6]],
        )
    )
    expected = dict(
        dfx=pd.DataFrame(
            {"A_c": [1], "A_d": [2], "A_e": [3], "B_c": [4], "B_d": [5], "B_e": [6]}
        )
    )
    config = ec.Config()
    return outbound, expected, config


def get_time_str() -> str:
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d-%H%M%S-%f")


def push(
    test_medium,
    outbound,
    config=ec.Config(),
):
    config.source.url = el.urlize_dict(outbound)
    config.target.url = get_flight_url(test_medium)

    print(f"pushing {config.source.url} as {outbound}")
    th.config_execute(config, f"{get_time_str()}_push.els.yml")


def pull(
    test_medium,
    inbound=None,
    config=ec.Config(),
):
    if inbound is None:
        inbound = {}
    # if test_medium not in ("csv"):
    config.source.url = get_flight_url(test_medium)
    # else:
    # config.source.url = None
    config.target.url = el.urlize_dict(inbound)

    print("pulling")
    th.config_execute(config, f"{get_time_str()}_pull.els.yml")
    return inbound
