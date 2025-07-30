#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016, Silvio Peroni <essepuntato@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.
from __future__ import annotations

import os
from shutil import copymode, move
from tempfile import mkstemp
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import BinaryIO, Tuple, List, Dict

from oc_ocdm.counter_handler.counter_handler import CounterHandler
from oc_ocdm.support.support import is_string_empty


class FilesystemCounterHandler(CounterHandler):
    """A concrete implementation of the ``CounterHandler`` interface that persistently stores
    the counter values within the filesystem."""

    _initial_line_len: int = 3
    _trailing_char: str = " "

    def __init__(self, info_dir: str, supplier_prefix: str = "") -> None:
        """
        Constructor of the ``FilesystemCounterHandler`` class.

        :param info_dir: The path to the folder that does/will contain the counter values.
        :type info_dir: str
        :raises ValueError: if ``info_dir`` is None or an empty string.
        """
        if info_dir is None or is_string_empty(info_dir):
            raise ValueError("info_dir parameter is required!")

        if info_dir[-1] != os.sep:
            info_dir += os.sep

        self.info_dir: str = info_dir
        self.supplier_prefix: str = supplier_prefix
        self.datasets_dir: str = info_dir + 'datasets' + os.sep
        self.short_names: List[str] = ["an", "ar", "be", "br", "ci", "de", "id", "pl", "ra", "re", "rp"]
        self.metadata_short_names: List[str] = ["di"]
        self.info_files: Dict[str, str] = {key: ("info_file_" + key + ".txt")
                                           for key in self.short_names}
        self.prov_files: Dict[str, str] = {key: ("prov_file_" + key + ".txt")
                                           for key in self.short_names}

    def set_counter(self, new_value: int, entity_short_name: str, prov_short_name: str = "",
                    identifier: int = 1, supplier_prefix: str = "") -> None:
        """
        It allows to set the counter value of graph and provenance entities.

        :param new_value: The new counter value to be set
        :type new_value: int
        :param entity_short_name: The short name associated either to the type of the entity itself
         or, in case of a provenance entity, to the type of the relative graph entity.
        :type entity_short_name: str
        :param prov_short_name: In case of a provenance entity, the short name associated to the type
         of the entity itself. An empty string otherwise.
        :type prov_short_name: str
        :param identifier: In case of a provenance entity, the counter value that identifies the relative
          graph entity. The integer value '1' otherwise.
        :type identifier: int
        :raises ValueError: if ``new_value`` is a negative integer or ``identifier`` is less than or equal to zero.
        :return: None
        """
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")

        if prov_short_name == "se":
            file_path: str = self._get_prov_path(entity_short_name, supplier_prefix)
        else:
            file_path: str = self._get_info_path(entity_short_name, supplier_prefix)
        self._set_number(new_value, file_path, identifier)

    def set_counters_batch(self, updates: Dict[Tuple[str, str], Dict[int, int]], supplier_prefix: str) -> None:
        """
        Updates counters in batch for multiple files.
        `updates` is a dictionary where the key is a tuple (entity_short_name, prov_short_name)
        and the value is a dictionary of line numbers to new counter values.
        """
        for (entity_short_name, prov_short_name), file_updates in updates.items():
            file_path = self._get_prov_path(entity_short_name, supplier_prefix) if prov_short_name == "se" else self._get_info_path(entity_short_name, supplier_prefix)
            self._set_numbers(file_path, file_updates)

    def _set_numbers(self, file_path: str, updates: Dict[int, int]) -> None:
        """
        Apply multiple counter updates to a single file.
        `updates` is a dictionary where the key is the line number (identifier)
        and the value is the new counter value.
        """
        self.__initialize_file_if_not_existing(file_path)
        with open(file_path, 'r') as file:
            lines = file.readlines()
        max_line_number = max(updates.keys())

        # Ensure the lines list is long enough
        while len(lines) < max_line_number + 1:
            lines.append("\n")  # Default counter value

        # Apply updates
        for line_number, new_value in updates.items():
            lines[line_number-1] = str(new_value).rstrip() + "\n"

        # Write updated lines back to file
        with open(file_path, 'w') as file:
            file.writelines(lines)

    def read_counter(self, entity_short_name: str, prov_short_name: str = "", identifier: int = 1, supplier_prefix: str = "") -> int:
        """
        It allows to read the counter value of graph and provenance entities.

        :param entity_short_name: The short name associated either to the type of the entity itself
         or, in case of a provenance entity, to the type of the relative graph entity.
        :type entity_short_name: str
        :param prov_short_name: In case of a provenance entity, the short name associated to the type
         of the entity itself. An empty string otherwise.
        :type prov_short_name: str
        :param identifier: In case of a provenance entity, the counter value that identifies the relative
          graph entity. The integer value '1' otherwise.
        :type identifier: int
        :raises ValueError: if ``identifier`` is less than or equal to zero.
        :return: The requested counter value.
        """
        if prov_short_name == "se":
            file_path: str = self._get_prov_path(entity_short_name, supplier_prefix)
        else:
            file_path: str = self._get_info_path(entity_short_name, supplier_prefix)
        return self._read_number(file_path, identifier)

    def increment_counter(self, entity_short_name: str, prov_short_name: str = "", identifier: int = 1, supplier_prefix: str = "") -> int:
        """
        It allows to increment the counter value of graph and provenance entities by one unit.

        :param entity_short_name: The short name associated either to the type of the entity itself
         or, in case of a provenance entity, to the type of the relative graph entity.
        :type entity_short_name: str
        :param prov_short_name: In case of a provenance entity, the short name associated to the type
         of the entity itself. An empty string otherwise.
        :type prov_short_name: str
        :param identifier: In case of a provenance entity, the counter value that identifies the relative
          graph entity. The integer value '1' otherwise.
        :type identifier: int
        :raises ValueError: if ``identifier`` is less than or equal to zero.
        :return: The newly-updated (already incremented) counter value.
        """
        if prov_short_name == "se":
            file_path: str = self._get_prov_path(entity_short_name, supplier_prefix)
        else:
            file_path: str = self._get_info_path(entity_short_name, supplier_prefix)
        return self._add_number(file_path, identifier)

    def _get_info_path(self, short_name: str, supplier_prefix: str) -> str:
        supplier_prefix = "" if supplier_prefix is None else supplier_prefix
        directory = self.info_dir if supplier_prefix == self.supplier_prefix or not self.supplier_prefix else self.info_dir.replace(self.supplier_prefix, supplier_prefix, 1)
        return directory + self.info_files[short_name]

    def _get_prov_path(self, short_name: str, supplier_prefix: str) -> str:
        supplier_prefix = "" if supplier_prefix is None else supplier_prefix
        directory = self.info_dir if supplier_prefix == self.supplier_prefix or not self.supplier_prefix else self.info_dir.replace(self.supplier_prefix, supplier_prefix, 1)
        return directory + self.prov_files[short_name]

    def _get_metadata_path(self, short_name: str, dataset_name: str) -> str:
        return self.datasets_dir + dataset_name + os.sep + 'metadata_' + short_name + '.txt'

    def __initialize_file_if_not_existing(self, file_path: str):
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        if not os.path.isfile(file_path):
            with open(file_path, 'w') as file:
                file.write("\n")

    def _read_number(self, file_path: str, line_number: int) -> int:
        if line_number <= 0:
            raise ValueError("line_number must be a positive non-zero integer number!")

        self.__initialize_file_if_not_existing(file_path)

        cur_number: int = 0
        try:
            with open(file_path, 'r') as file:
                for i, line in enumerate(file, 1):
                    if i == line_number:
                        line = line.strip()
                        if line:
                            cur_number = int(line)
                        break
                else:
                    print(file_path)
        except ValueError as e:
            print(f"ValueError: {e}")
            cur_number = 0
        except Exception as e:
            print(f"Unexpected error: {e}")
        return cur_number

    def _add_number(self, file_path: str, line_number: int = 1) -> int:
        if line_number <= 0:
            raise ValueError("line_number must be a positive non-zero integer number!")

        self.__initialize_file_if_not_existing(file_path)

        current_value = self._read_number(file_path, line_number)
        new_value = current_value + 1
        self._set_number(new_value, file_path, line_number)
        return new_value

    def _set_number(self, new_value: int, file_path: str, line_number: int = 1) -> None:
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")

        if line_number <= 0:
            raise ValueError("line_number must be a positive non-zero integer number!")

        self.__initialize_file_if_not_existing(file_path)

        lines = []
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Ensure the file has enough lines
        while len(lines) < line_number:
            lines.append("\n")

        # Update the specific line
        lines[line_number - 1] = f"{new_value}\n"

        # Write back to the file
        with open(file_path, 'w') as file:
            file.writelines(lines)


    def set_metadata_counter(self, new_value: int, entity_short_name: str, dataset_name: str) -> None:
        """
        It allows to set the counter value of metadata entities.

        :param new_value: The new counter value to be set
        :type new_value: int
        :param entity_short_name: The short name associated either to the type of the entity itself.
        :type entity_short_name: str
        :param dataset_name: In case of a ``Dataset``, its name. Otherwise, the name of the relative dataset.
        :type dataset_name: str
        :raises ValueError: if ``new_value`` is a negative integer, ``dataset_name`` is None or
          ``entity_short_name`` is not a known metadata short name.
        :return: None
        """
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")

        if dataset_name is None:
            raise ValueError("dataset_name must be provided!")

        if entity_short_name not in self.metadata_short_names:
            raise ValueError("entity_short_name is not a known metadata short name!")

        file_path: str = self._get_metadata_path(entity_short_name, dataset_name)
        return self._set_number(new_value, file_path, 1)

    def read_metadata_counter(self, entity_short_name: str, dataset_name: str) -> int:
        """
        It allows to read the counter value of metadata entities.

        :param entity_short_name: The short name associated either to the type of the entity itself.
        :type entity_short_name: str
        :param dataset_name: In case of a ``Dataset``, its name. Otherwise, the name of the relative dataset.
        :type dataset_name: str
        :raises ValueError: if ``dataset_name`` is None or ``entity_short_name`` is not a known metadata short name.
        :return: The requested counter value.
        """
        if dataset_name is None:
            raise ValueError("dataset_name must be provided!")

        if entity_short_name not in self.metadata_short_names:
            raise ValueError("entity_short_name is not a known metadata short name!")

        file_path: str = self._get_metadata_path(entity_short_name, dataset_name)
        return self._read_number(file_path, 1)

    def increment_metadata_counter(self, entity_short_name: str, dataset_name: str) -> int:
        """
        It allows to increment the counter value of metadata entities by one unit.

        :param entity_short_name: The short name associated either to the type of the entity itself.
        :type entity_short_name: str
        :param dataset_name: In case of a ``Dataset``, its name. Otherwise, the name of the relative dataset.
        :type dataset_name: str
        :raises ValueError: if ``dataset_name`` is None or ``entity_short_name`` is not a known metadata short name.
        :return: The newly-updated (already incremented) counter value.
        """
        if dataset_name is None:
            raise ValueError("dataset_name must be provided!")

        if entity_short_name not in self.metadata_short_names:
            raise ValueError("entity_short_name is not a known metadata short name!")

        file_path: str = self._get_metadata_path(entity_short_name, dataset_name)
        return self._add_number(file_path, 1)