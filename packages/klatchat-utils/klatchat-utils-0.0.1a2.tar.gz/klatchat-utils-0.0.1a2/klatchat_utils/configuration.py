# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import json

from abc import ABC, abstractmethod
from typing import Tuple, Optional, Any
from ovos_config.config import Configuration
from ovos_utils.log import LOG, deprecated

from klatchat_utils.exceptions import MalformedConfigurationException


class KlatConfigurationBase(ABC):
    """Generic configuration module"""

    def __init__(self):
        self._config_data: Optional[dict] = None
        self._init_ovos_config()
        if not self._config_data:
            LOG.warning(
                f"OVOS Config does not contain required key = {self.config_key}, "
                f"trying setting up legacy config"
            )
            self._init_legacy_config()
        self.validate_provided_configuration()
        # init_log_aggregators(config=self.config_data)

    @property
    def config_data(self) -> dict:
        if not self._config_data:
            self._config_data = dict()
        return self._config_data

    @config_data.setter
    def config_data(self, value: dict):
        if not isinstance(value, dict):
            raise TypeError(f"Type: {type(value)} not supported")
        self._config_data = value

    @property
    @abstractmethod
    def required_sub_keys(self) -> Tuple[str]:
        """
        Override to specify required configuration parameters for this module
        """
        pass

    @property
    @abstractmethod
    def config_key(self) -> str:
        """
        Override to specify the top-level configuration key associated with this
        module.
        """
        pass

    def _init_ovos_config(self):
        ovos_config = Configuration()
        if self.config_key in ovos_config:
            self._config_data = ovos_config.get(self.config_key)

    @deprecated("Legacy configuration is deprecated",
                "0.0.1")
    def _init_legacy_config(self):
        try:
            legacy_config_path = os.path.expanduser(
                os.environ.get(
                    f"{self.config_key}_CONFIG",
                    "~/.local/share/neon/credentials.json"
                )
            )
            self.add_new_config_properties(
                self.extract_config_from_path(legacy_config_path)
            )
            self._config_data = self._config_data[self.config_key]
        except KeyError as e:
            raise MalformedConfigurationException(e)

    def validate_provided_configuration(self):
        for key in self.required_sub_keys:
            if key not in self._config_data:
                raise MalformedConfigurationException(
                    f"Required configuration {key=!r} is missing")

    def add_new_config_properties(self, new_config_dict: dict,
                                  at_key: Optional[str] = None):
        """
        Adds new configuration properties to existing configuration dict. This
        does not modify the configuration on-disk, so changes WILL NOT persist.
        :param new_config_dict: dictionary containing new configuration
        :param at_key: If specified, set configuration at that key to the new
          value, else merge the new value with the existing configuration
        """
        if at_key:
            self.config_data[at_key] = new_config_dict
        else:
            # merge existing config with new dictionary (python 3.5+ syntax)
            self.config_data |= new_config_dict

    def get(self, key: str, default: Any = None):
        return self.config_data.get(key, default)

    def __getitem__(self, key):
        return self.config_data.get(key)

    def __setitem__(self, key, value):
        self.config_data[key] = value

    @staticmethod
    def extract_config_from_path(file_path: str) -> dict:
        """
        Extracts configuration dictionary from desired file path

        :param file_path: desired file path

        :returns dictionary containing configs from target file, empty dict otherwise
        """
        try:
            with open(os.path.expanduser(file_path)) as input_file:
                extraction_result = json.load(input_file)
        except Exception as ex:
            LOG.error(
                f"Exception occurred while extracting data from {file_path}: {ex}"
            )
            extraction_result = dict()
        # LOG.info(f'Extracted config: {extraction_result}')
        return extraction_result
