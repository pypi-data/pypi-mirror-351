from __future__ import annotations

import logging
import os
import sys
from copy import deepcopy
from enum import Enum
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from stat import FILE_ATTRIBUTE_HIDDEN  # type:ignore
from typing import TYPE_CHECKING, Any, NamedTuple, Optional, Union

import typer
import yaml
from anytree import NodeMixin, PreOrderIter, RenderTree  # type:ignore

import els.config as ec
import els.core as el
import els.execute as ee
import els.flow as ef
from els._typing import listify
from els.pathprops import HumanPathPropertiesMixin

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping, MutableMapping

    import els.io.base as eio

CONFIG_FILE_EXT = ".els.yml"
FOLDER_CONFIG_FILE_STEM = "_"
ROOT_CONFIG_FILE_STEM = "__"


class FlowAtom(NamedTuple):
    # first two attributes cannot change relative position
    source_url: str
    source_container_class: type[eio.ContainerProtocol]
    ###
    config: ec.Config


class NodeType(Enum):
    CONFIG_DIRECTORY = "config directory"
    CONFIG_EXPLICIT = "explicit config"
    CONFIG_ADJACENT = "adjacent config"
    CONFIG_VIRTUAL = "virtual config"
    # CONFIG_DOC = "config_doc"
    DATA_URL = "source url"
    DATA_TABLE = "data_table"


class FileType(Enum):
    EXCEL = "excel"
    CSV = "csv"
    ELS = "els"
    FWF = "fixed width file"
    XML = "xml"
    PDF = "pdf"

    @classmethod
    def suffix_to_type(
        cls,
        extension: str,
    ) -> Optional[FileType]:
        mapping = {
            "xlsx": cls.EXCEL,
            "xls": cls.EXCEL,
            "xlsm": cls.EXCEL,
            "xlsb": cls.EXCEL,
            "csv": cls.CSV,
            "tsv": cls.CSV,
            # TODO: handle double extension els.yml
            # for now assumes any yml file is an els config
            "yml": cls.ELS,
            "fwf": cls.FWF,
            "xml": cls.XML,
            "pdf": cls.PDF,
        }
        return mapping.get(extension.lower().strip("."), None)


def get_dir_config_name() -> str:
    return FOLDER_CONFIG_FILE_STEM + CONFIG_FILE_EXT


def get_root_config_name() -> str:
    return ROOT_CONFIG_FILE_STEM + CONFIG_FILE_EXT


class ConfigPath(Path, HumanPathPropertiesMixin, NodeMixin):
    # subclassing pathlib.Path not supported until Python 3.12
    if sys.version_info < (3, 12):
        _flavour = type(Path())._flavour  # type:ignore

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if sys.version_info < (3, 12):
            pass
        else:
            super().__init__(*args, **kwargs)
        self.config_local: Optional[ec.Config] = None

    # called from plant_tree() to build:
    #  (1) individual inheritance chain nodes without walking
    #  (2) configuration context node with walking
    # called from grow_dir_branches() to build
    #  (1) config file nodes
    #  (2) config dir nodes
    def configure_node(
        self,
        walk_dir: Optional[bool] = False,
    ) -> None:
        if self.is_dir():
            self.config = self.dir_config

            if walk_dir:
                self.grow_dir_branches()
                if not self.has_leaf_table:
                    # do not add dirs with no leaf nodes which are tables
                    self.parent = None
        elif self.is_config_file:  # type:ignore
            self.config = ec.Config(source=ec.Source(url=self.adjacent_file_path))
            self.grow_config_branches()
        else:
            raise Exception("Unknown node cannot be configured.")

    @property
    def children(self) -> tuple[ConfigPath]:
        return super().children

    def grow_dir_branches(self) -> None:
        for subpath in self.glob("*"):
            # ensure node-level configs are not (double) counted
            if (
                subpath.name
                in (
                    get_dir_config_name(),
                    get_root_config_name(),
                )
                or subpath in self.children
                or ConfigPath(str(subpath) + CONFIG_FILE_EXT) in self.children
            ):
                pass
            elif config_path_valid(subpath):
                if subpath.is_dir() or subpath.is_config_file():  # adjecent config
                    cpath = subpath
                else:  # directory or explicit config file
                    cpath = ConfigPath(str(subpath) + CONFIG_FILE_EXT)
                cpath.parent = self
                cpath.configure_node(walk_dir=True)
            else:
                logging.warning(f"Invalid path not added to tree: {str(subpath)}")

    @property
    def dir_config(self) -> ec.Config:
        configs: list[Union[ec.Config, dict[str, Any]]] = []

        # a dir can have root config and/or dir config
        if self.is_root_dir:
            config_path = Path(self) / get_root_config_name()
            if config_path.exists():
                ymls = get_yml_docs(config_path, expected=1)
                configs.append(ymls[0])

        if self.is_dir():
            config_path = Path(self) / get_dir_config_name()
            if config_path.exists():
                ymls = get_yml_docs(config_path, expected=1)
                configs.append(ymls[0])
            # if both root and dir config found, merge
            if len(configs) > 0:
                return ec.merge_configs(*configs)
            else:
                return ec.Config()
        else:
            raise Exception("dir_config called on a non-directory node.")

    @property
    def paired_config(self) -> list[ec.Config]:
        if self.node_type != NodeType.CONFIG_VIRTUAL:
            docs = get_yml_docs(self)

            # adjacent can have an explicit url if it matches adjacent
            first_config = ec.Config.model_validate(docs[0])
            if (
                self.node_type == NodeType.CONFIG_ADJACENT
                and first_config.source.url
                and first_config.source.url != self.adjacent_file_path
            ):
                raise Exception(
                    f"adjacent config {self} has url: {first_config.source.url} "
                    "different than its adjacent data file: "
                    f"{self.adjacent_file_path}"
                )
            elif first_config.source.url and "*" in first_config.source.url:
                docs.clear()
                if not first_config.source.table:
                    for p in Path(self).parent.glob(first_config.source.url):
                        first_config_copy: ec.Config = deepcopy(first_config)
                        first_config_copy.source.url = str(p)
                        docs.append(first_config_copy)
                else:
                    tables = listify(first_config.source.table)
                    for t in tables:
                        first_config_copy = deepcopy(first_config)
                        first_config_copy.source.url = first_config.source.url.replace(
                            "*", t
                        )
                        docs.append(first_config_copy)
            return [ec.Config.model_validate(c) for c in docs]
        elif self.config_local:
            return [self.config_local]
        else:  # NodeType.CONFIG_VIRTUAL has no explicit config
            return [ec.Config()]

    def get_table_docs(
        self,
        source: ec.Source,
        url_parent: ConfigPath,
        config: ec.Config,
    ) -> dict[str, ec.Config]:
        table_docs: dict[str, ec.Config] = dict()
        if (
            self.node_type
            in (
                NodeType.CONFIG_ADJACENT,
                NodeType.CONFIG_VIRTUAL,
            )
            or not source.table
        ):
            leafs_names = get_content_leaf_names(url_parent.config.source)
            if leafs_names:
                for content_table in leafs_names:
                    if not source.table or source.table == content_table:
                        config = config.merge_with(
                            ec.Config(source=ec.Source(table=content_table)),
                        )
                        table_docs[content_table] = config
            else:
                raise Exception(
                    f"No leafs found ({leafs_names}) in {url_parent.config.source}."
                )
        else:
            for t in source.table_list:
                if (
                    # TODO: make this dynamic
                    source.type in (".csv", ".xml")
                    and source.url
                    and not t == source.url.split("/")[-1].split(".")[0]
                ):
                    continue
                config_copy = config.model_copy(deep=True)
                config_copy.source.table = t
                table_docs[t] = config_copy
        return table_docs

    def transform_splits(
        self,
        config: ec.Config,
        ca_path: ConfigPath,
    ) -> None:
        if config.transforms_affect_target_count:
            transforms = config.transforms_to_determine_target

            remaining_transforms_count = len(transforms) - len(config.transform_list)
            if remaining_transforms_count < 0:
                remaining_transforms = config.transform_list[
                    remaining_transforms_count:
                ]
            else:
                remaining_transforms = []

            df = ee.pull_frame(config.source)
            if df.empty:
                raise Exception(
                    f"Empty dataframe when transforming splits on {config.source.url}"
                )
            df_dict = None
            if len(transforms) > 1:
                df = ee.apply_transforms(df, transforms=transforms[:-1])
                df_dict = dict(transformed=df)
            assert isinstance(transforms[-1], ec.SplitOnColumn)
            split_transform = transforms[-1]
            split_on_column = split_transform.split_on_column
            sub_tables: list[Union[str, int, float]] = split_transform(df)  # type:ignore
            for sub_table in sub_tables:
                if isinstance(sub_table, str):
                    column_eq: Union[str, float, int] = f"'{sub_table}'"
                    table_name = sub_table
                else:
                    column_eq = sub_table
                    table_name = f"{split_on_column}_{sub_table}"
                filter = f"{split_on_column} == {column_eq}"
                sub_table_path = ca_path / filter
                sub_table_path.parent = ca_path
                sub_table_path.config_local = ec.Config(
                    target=ec.Target(table=table_name),
                    transforms=[ec.FilterTransform(filter=filter)]
                    + remaining_transforms,
                )
                if df_dict:
                    sub_table_path.config_local.source.table = "transformed"
                    sub_table_path.config_local.source.url = el.urlize_dict(df_dict)

    def grow_config_branches(self) -> None:
        previous_url = ""
        for config in self.paired_config:
            merged_doc = self.config.merge_with(config)
            source = merged_doc.source

            if source.url and source.url != previous_url:
                previous_url = source.url
                url_parent = ConfigPath(Path(previous_url))
                url_parent.parent = self
                url_parent.config_local = config
            else:
                raise Exception("Unable to grow config branches")

            if previous_url == "":
                raise Exception("expected to have a url for child config doc")
            table_docs = self.get_table_docs(source, url_parent, config)

            for tab, config in table_docs.items():
                ca_path = ConfigPath(Path(previous_url) / tab)
                ca_path.parent = url_parent
                ca_path.config_local = config
                self.transform_splits(config, ca_path)
        # This for block splits read args in lists into individual nodes
        for leaf in self.leaves:
            if (
                leaf.config.source
                and leaf.config.source.read_args
                and isinstance(leaf.config.source.read_args, list)
            ):
                # TODO: not sure why this is not working
                # if len(leaf.config.source.read_x) == 1:
                #     leaf.config.source.read_x = leaf.config.source.read_x[0]
                # else:
                for i, kw in enumerate(leaf.config.source.read_args):
                    subset = ConfigPath(leaf / f"subset_{i}")
                    subset.parent = leaf
                    subset.config_local = leaf.config
                    subset.config_local.source.read_args = kw

    @property
    def node_type(self) -> NodeType:
        if self.is_dir():
            return NodeType.CONFIG_DIRECTORY
        elif self.is_config_file():
            if self.is_file():
                if Path(str(self).replace(CONFIG_FILE_EXT, "")).is_file():
                    return NodeType.CONFIG_ADJACENT
                else:
                    return NodeType.CONFIG_EXPLICIT
            else:
                return NodeType.CONFIG_VIRTUAL
        elif self.is_file():
            return NodeType.DATA_URL
        elif self.parent.is_config_file():
            return NodeType.DATA_URL
        else:
            return NodeType.DATA_TABLE

    @property
    def leaves(self) -> tuple[ConfigPath]:
        return super().leaves

    @property
    def get_leaf_tables(self) -> list[ConfigPath]:
        leaf_tables: list[ConfigPath] = []
        for leaf in self.leaves:
            if leaf.node_type == NodeType.DATA_TABLE:
                leaf_tables.append(leaf)
        return leaf_tables

    @property
    def has_leaf_table(self) -> bool:
        return not self.get_leaf_tables

    @property
    def ancestors_to_self(self) -> tuple[ConfigPath]:
        return self.ancestors + (self,)

    @property
    def config_file_path(self) -> str:
        if self.node_type == NodeType.CONFIG_DIRECTORY:
            if self.is_root:
                return f"{self.abs}\\{get_root_config_name()}"
            else:
                return f"{self.abs}\\{get_dir_config_name()}"
        elif (
            self.node_type == NodeType.CONFIG_EXPLICIT
            or self.node_type == NodeType.CONFIG_VIRTUAL
            or self.node_type == NodeType.CONFIG_ADJACENT
        ):
            return str(self.abs)
        elif self.node_type == NodeType.DATA_URL:
            return str(self.parent.abs)
        elif self.node_type == NodeType.DATA_TABLE:
            return str(self.parent.parent.abs)
        else:
            raise Exception("config file path not found")

    def config_raw(
        self,
        add_config_file_path: bool = False,
    ) -> ec.Config:
        config_line: list[dict[str, Any]] = []
        # if root els config is mandatory, this "default dump line" is not required
        config_line.append(ec.Config().model_dump(exclude_none=True))

        for node in self.ancestors_to_self:
            if node.config_local is not None:
                config_line.append(node.config_local.model_dump(exclude_none=True))

        config_merged = ec.merge_configs(*config_line)
        config_copied = config_merged.model_copy(deep=True)

        # Useful when printing/debugging yamls:
        if add_config_file_path:
            config_copied.config_path = self.config_file_path

        return config_copied

    @property
    def config(self) -> ec.Config:
        config_copied = self.config_raw()
        # config_evaled = config_copied
        config_evaled = self.eval_dynamic_attributes(config_copied)

        if self.node_type == NodeType.DATA_TABLE:
            if not config_evaled.target.if_exists:
                config_evaled.target.if_exists = "fail"

            if not config_evaled.target.table:
                config_evaled.target.table = self.name

        return config_evaled

    @config.setter
    def config(self, config: ec.Config) -> None:
        self.config_local = config

    def get_path_props_find_replace(self) -> dict[str, str]:
        res: dict[str, str] = {}
        for member in ec.DynamicPathValue:  # type:ignore
            path_val = getattr(self, member.value[1:])
            res[member.value] = path_val
        return res

    def eval_dynamic_attributes(self, config: ec.Config) -> ec.Config:
        config_dict = config.model_dump(exclude_none=True)
        find_replace = self.get_path_props_find_replace()
        if (
            self.is_leaf
            and config_dict
            and "target" in config_dict
            and "table" in config_dict["target"]
            and "url" in config_dict["target"]
            and "*" in config_dict["target"]["url"]
        ):
            config_dict["target"]["url"] = config_dict["target"]["url"].replace(
                "*", config_dict["target"]["table"]
            )

        ConfigPath.swap_dict_vals(config_dict, find_replace)
        res = ec.Config(**config_dict)
        return res

    @staticmethod
    def is_dict_of_dfs(_dict: dict[Any, Any]) -> bool:
        for k, v in _dict:
            if isinstance(k, str):
                pass
            else:
                return False
        return True

    @staticmethod
    def swap_dict_vals(
        dictionary: MutableMapping[str, Any],
        find_replace_dict: MutableMapping[str, str],
    ) -> None:
        for key, value in dictionary.items():
            if isinstance(value, dict):
                ConfigPath.swap_dict_vals(dictionary[key], find_replace_dict)
            elif isinstance(value, list) or (
                isinstance(value, dict) and ConfigPath.is_dict_of_dfs(value)
            ):
                pass
            elif value in find_replace_dict:
                dictionary[key] = find_replace_dict[value]
            elif isinstance(value, str) and key == "url" and "*" in value:
                dictionary[key] = value.replace("*", find_replace_dict["_leaf_name"])

    @property
    def is_root_dir(self) -> bool:
        return self.is_dir() and self.is_root

    @property
    def adjacent_file_path(self) -> str:
        return str(Path(str(self).replace(CONFIG_FILE_EXT, "")))

    def RenderTreeTyped(self) -> Iterable[tuple[str, ConfigPath]]:
        for pre, _, node in RenderTree(self):
            yield pre, node

    def display_tree(self) -> None:
        column1_width = 0
        column2_width = 0
        rows: list[tuple[str, str]] = []
        # for pre, fill, node in RenderTree(self):
        for pre, node in self.RenderTreeTyped():
            column2 = ""
            if node.is_root and node.is_dir():
                column1 = f"{pre}{str(node.abs.name)}"
            elif node.node_type == NodeType.DATA_TABLE:
                column1 = f"{pre}{node.name}"
            # TODO: this might be useful
            # elif node.node_type == NodeType.DATA_URL:
            #     column1 = f"{pre}{node.config.source.url}"
            elif node.node_type == NodeType.DATA_URL and (
                node.config.source.url and not Path(node.config.source.url).exists()
            ):
                url_branch = (
                    str(node.path[-1])
                    .split("?")[0]
                    .replace("\\", "/")
                    .replace(":", ":/")
                )
                column1 = f"{pre}{url_branch}"
            else:
                column1 = f"{pre}{node.name}"
            if (
                node.node_type == NodeType.DATA_TABLE and node.config.target.url
            ) and not node.config.target.type == "dict":
                # TODO: replace hard-coded types
                if node.config.target.type in (".csv", ".xml"):
                    target_path = os.path.relpath(node.config.target.url)
                else:
                    target_path = f"{node.config.target.url.split('?')[0]}#{node.config.target.table}"

                column2 = f" → {target_path}"
            elif node.is_leaf and (node.config.target.type == "dict"):
                column2 = f" → stdout://#{node.config.target.table}"

            rows.append((column1, column2))

            if column2 != "":  # only count if there is a second column
                column1_width = max(column1_width, len(column1))
                column2_width = max(column2_width, len(column2))

        for column1, column2 in rows:
            typer.echo(f"{column1:{column1_width}}{column2}".rstrip())

    @property
    def parent(self):  # type:ignore
        if NodeMixin.parent.fget is not None:
            return NodeMixin.parent.fget(self)
        else:
            return self

    @parent.setter
    def parent(self, value: Optional[ConfigPath]) -> None:
        if NodeMixin.parent.fset:
            NodeMixin.parent.fset(self, value)

    @property
    def root_node(self) -> ConfigPath:
        if NodeMixin.root.fget:
            return NodeMixin.root.fget(self)
        else:
            return self

    def is_config_file(self) -> bool:
        return str(self).endswith(CONFIG_FILE_EXT)

    # TODO, dead code, consider ressurecting support for wildcards
    # @property
    # def subdir_patterns(self) -> list[str]:
    #     # TODO patterns may overlap
    #     children = self.config_local.children
    #     if children is None or children == {}:
    #         res = ["*"]
    #     elif isinstance(children, str):
    #         res = [str(children)]  # recasting as str for linter
    #     elif isinstance(children, dict):
    #         # get key of each dict as list entries
    #         res = list(children.keys())
    #     elif isinstance(children, list):
    #         res = children
    #     # if list of dicts
    #     else:
    #         raise Exception("Unexpected children")
    #     return res

    def get_url_leaf_names(self) -> list[str]:
        if self.config.source.url:
            return [self.config.source.url]
        else:
            raise Exception("No url leaf names to get")

    def is_hidden(self) -> bool:
        """Check if the given Path object is hidden."""
        # Check for UNIX-like hidden files/directories
        if self.name.startswith("."):
            return True

        # Check for Windows hidden files/directories
        if os.name == "nt":
            try:
                attrs = os.stat(self)
                return bool(attrs.st_file_attributes & FILE_ATTRIBUTE_HIDDEN)  # type:ignore
            except AttributeError:
                # If FILE_ATTRIBUTE_HIDDEN not defined,
                # assume it's not hidden
                pass

        return False

    @property
    def abs(self) -> ConfigPath:
        return ConfigPath(self.absolute())

    @property  # fs = filesystem, can return a File or Dir but not content
    def fs(self) -> ConfigPath:
        if self.node_type == NodeType.DATA_TABLE:
            res = self.parent
        else:
            res = self
        return res

    @property
    def dir(self) -> Path:
        if self.node_type == NodeType.DATA_TABLE and self.parent:
            res = self.parent.dir
        elif self.is_file():
            if self.parent:
                res = self.parent
            else:
                res = Path(self).parent
        else:
            res = self
        return res

    @property
    def file(self) -> Optional[ConfigPath]:
        if self.node_type == NodeType.DATA_TABLE:
            res = self.parent
        elif self.is_file():
            res = self
        else:
            res = None
        return res

    @property
    def ext(self) -> str:
        file = self.file
        if file:
            return file.suffix
        else:
            return ""

    @staticmethod
    def apply_file_wrappers(
        parent: Optional[ef.FlowNodeMixin],
        flow_atoms: Iterable[FlowAtom],
        execute_fn: Callable[[ec.Config], bool],
    ) -> None:
        ingest_files = ef.ElsFlow(parent=parent, n_jobs=1)
        keys = itemgetter(0, 1)
        flow_atoms = sorted(
            flow_atoms,
            key=keys,
        )
        for url_container, atoms in groupby(
            flow_atoms,
            keys,
        ):
            file_wrapper = ef.ElsContainerWrapper(
                parent=ingest_files,
                url=url_container[0],
                container_class=url_container[1],
            )
            exe_flow = ef.ElsFlow(parent=file_wrapper, n_jobs=1)
            for atom in atoms:
                ef.ElsExecute(
                    parent=exe_flow,
                    name=atom.source_url,
                    config=atom.config,
                    execute_fn=execute_fn,
                )

    @property
    def target_table_flow_atoms(self) -> dict[str, list[FlowAtom]]:
        res: dict[str, list[FlowAtom]] = {}
        for leaf in self.leaves:
            if leaf.node_type == NodeType.DATA_TABLE:
                assert isinstance(leaf.config.target.table, str)
                assert isinstance(leaf.config.source.url, str)
                res.setdefault(leaf.config.target.table, []).append(
                    FlowAtom(
                        source_url=leaf.config.source.url,
                        source_container_class=ee.get_container_class(
                            leaf.config.source
                        ),
                        # TODO, should consider when same table name exists in different targets?
                        # target_table=leaf.config.target.table,
                        # load_parallel=leaf.config.source.load_parallel,
                        config=leaf.config,
                    )
                )
        return res

    def get_ingest_taskflow(self) -> ef.ElsFlow:
        root_flow = ef.ElsFlow()
        tt_flow_atoms = self.target_table_flow_atoms
        for target_table, flow_atoms in tt_flow_atoms.items():
            file_group_wrapper = ef.ElsTargetTableWrapper(
                parent=root_flow, name=target_table
            )
            ConfigPath.apply_file_wrappers(
                parent=file_group_wrapper, flow_atoms=flow_atoms, execute_fn=ee.ingest
            )
        return root_flow

    def get_els_yml_preview(self, diff: bool = True) -> list[dict[str, Any]]:
        ymls: list[dict[str, Any]] = []
        # for path, node in self.index.items():
        for node in [node for node in self.then_descendants]:
            if node.node_type != NodeType.CONFIG_VIRTUAL:
                node_config = node.config_raw(True).model_dump(
                    # TODO: excluding load_parallel for demo
                    exclude_none=True,
                    exclude={"source": {"load_parallel"}},
                )
                if node.is_root:
                    save_yml_dict = node_config
                elif diff:
                    if node.parent.node_type != NodeType.CONFIG_VIRTUAL:
                        parent_config = node.parent.config_raw(True).model_dump(
                            exclude_none=True
                        )
                    else:
                        parent_config = node.parent.parent.config_raw(True).model_dump(
                            exclude_none=True
                        )
                    save_yml_dict = mapping_diff(parent_config, node_config)
                else:
                    save_yml_dict = node_config
                if save_yml_dict:
                    ymls.append(save_yml_dict)
        return ymls
        # save_path = self.root.path / self.CONFIG_PREVIEW_FILE_NAME
        # with save_path.open("w", encoding="utf-8") as file:
        #     yaml.safe_dump_all(ymls, file, sort_keys=False, allow_unicode=True)

    @property
    def then_descendants(self) -> tuple[ConfigPath]:
        return PreOrderIter(self)

    def set_pandas_target(self, force: bool = False) -> None:
        # iterate all branches and leaves
        for node in self.then_descendants:
            # remove target from config
            if type(node.config_local) is not ec.Config:
                node.config_local = ec.Config.model_validate(node.config_local)
            if force or not node.config.target.url:
                node.config_local.target.url = el.urlize_dict(el.default_target)

    def set_nrows(self, nrows: int) -> None:
        for node in self.then_descendants:
            assert node.config_local
            node.config_local.source.nrows = nrows


def get_root_inheritance(dir_path: Optional[str] = None) -> list[Path]:
    if dir_path:
        start_dir = Path(dir_path)
    else:
        start_dir = Path()

    dirs: list[Path] = []
    current_dir = start_dir.absolute()
    file_found = False

    while (
        current_dir != current_dir.parent
    ):  # This condition ensures we haven't reached the root
        dirs.append(current_dir)
        if (current_dir / get_root_config_name()).exists():
            file_found = True
            break
        current_dir = current_dir.parent

    # Check and add the root directory if not already added
    if current_dir not in dirs and (current_dir / get_root_config_name()).exists():
        dirs.append(current_dir)
        file_found = True
    if file_found:
        return dirs
    else:
        glob_pattern = f"**/*{get_root_config_name()}"
        below = sorted(start_dir.glob(glob_pattern))
        if len(below) > 0:
            return [Path(below[0].parent.absolute())]
        else:
            logging.info(f"els root not found, using {start_dir}")
            if (
                start_dir.is_file()
                and (start_dir.parent / get_dir_config_name()).exists()
            ):
                return [start_dir, start_dir.parent]
            elif (
                not start_dir.exists()
                and (start_dir.parent / get_dir_config_name()).exists()
            ):
                return [start_dir, start_dir.parent]
            else:
                return [start_dir]


def plant_memory_tree(
    path: Path,
    memory_config: ec.Config,
) -> ConfigPath:
    ca_path = ConfigPath(path)
    ca_path.config = memory_config
    ca_path.grow_config_branches()
    return ca_path


def plant_tree(
    path: Path,
) -> ConfigPath:
    root_paths = list(reversed(get_root_inheritance(str(path))))
    root_path = Path(root_paths[0])
    if root_path.is_dir():
        os.chdir(root_path)
        # TODO: understand this better
        # seemingly redundant lines below fix strange bug when passing a directory as an
        # argument it got duplicated in the path, i.e. /foo/bar/bar when just /foo/bar
        # expected
        root_path = Path()
        root_paths[0] = Path()
    # else:
    #     os.chdir(root_path.parent)
    parent = None
    ca_path = None
    for index, path_ in enumerate(root_paths):
        if config_path_valid(path_):
            ca_path = ConfigPath(path_)
            ca_path.parent = parent
            # for the nodes in-between context and root, don't walk_dir
            if index < len(root_paths) - 1:
                ca_path.configure_node()
                parent = ca_path
            else:  # For the last item always process configs
                ca_path.configure_node(walk_dir=True)
        else:
            raise Exception("Invalid file in explicit path: " + str(path_))
    assert ca_path
    logging.info("Tree Created")
    root = parent.root_node if parent else ca_path
    if root.is_leaf and root.is_dir():
        logging.error("Root is an empty directory")
    return root


def mapping_diff(
    mapping1: Mapping[str, Any],
    mapping2: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Return elements that are in dict2 but not in dict1.

    :param dict1: First dictionary
    :param dict2: Second dictionary
    :return: A dictionary with elements only from dict2 that are not in dict1
    """
    diff: dict[Any, Any] = {}

    for key, value in mapping2.items():
        # If key is not present in mapping1, add the item
        if key not in mapping1:
            diff[key] = value
        # If key is present in both maps and both values are maps, recurse
        elif isinstance(value, dict) and isinstance(mapping1[key], dict):
            nested_diff = mapping_diff(mapping1[key], value)
            if nested_diff:
                diff[key] = nested_diff
        elif mapping1[key] != value:
            diff[key] = value

    return diff


def get_yml_docs(
    path: Union[ConfigPath, Path],
    expected: Optional[int] = None,
) -> list[
    Union[dict[str, Any], ec.Config]
]:  # including ec.Config in Union satisfies return
    if path.exists():
        with path.open() as file:
            yaml_text = file.read()
            documents = list(yaml.safe_load_all(yaml_text))
    else:
        raise Exception(f"path does not exist: {path}")
    # elif str(path).endswith(CONFIG_FILE_EXT):
    #     documents = [{"source": {"url": str(path).removesuffix(CONFIG_FILE_EXT)}}]

    # configs are loaded only to ensure they conform with yml schema
    _ = ymls_to_configs(documents)

    if expected is None or len(documents) == expected:
        return documents
    else:
        raise Exception(
            f"unexpected number of documents in {path}; expected: {expected}; found: {len(documents)}"
        )


def ymls_to_configs(ymls: Iterable[Mapping[str, Any]]) -> list[ec.Config]:
    configs: list[ec.Config] = []
    for yml in ymls:
        config = ec.Config(**yml)
        configs.append(config)
    return configs


def config_path_valid(path: Path) -> bool:
    if path.is_dir():
        return True
    if path.is_file() or ConfigPath(path).is_config_file():
        file_type = FileType.suffix_to_type(path.suffix)
        if isinstance(file_type, FileType):
            return True
    return False


def get_content_leaf_names(source: ec.Source) -> list[str]:
    assert source.url
    if source.type_is_excel or source.type_is_db or source.type == "dict":
        container_class = ee.get_container_class(source)
        container = el.fetch_df_container(container_class, source.url)
        return container.child_names
    elif source.type in (".csv", ".tsv", ".fwf", ".xml", ".pdf"):
        # return root file name without path and suffix
        res = [Path(source.url).stem]
        return res
    else:
        return [source.url]
