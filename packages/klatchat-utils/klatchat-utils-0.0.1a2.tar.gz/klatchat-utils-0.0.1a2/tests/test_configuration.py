# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
# Authors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3
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

from unittest import TestCase
from unittest.mock import patch

from klatchat_utils.configuration import KlatConfigurationBase
from klatchat_utils.exceptions import MalformedConfigurationException


class MockConfig(KlatConfigurationBase):
    @property
    def config_key(self) -> str:
        return "MOCK_MODULE"

    @property
    def required_sub_keys(self):
        return "test", "key"


mock_valid_configuration = {
    "MOCK_MODULE": {"test": True,
                    "key": "value",
                    "extra": "config"},
    "OTHER_MODULE": {}
}

mock_missing_top_key = {
    "OTHER_MODULE": {"test": True,
                     "key": "value",
                     "extra": "config"},
}

mock_missing_sub_key = {
    "MOCK_MODULE": {"key": "value",
                    "extra": "config"}
}


class TestConfiguration(TestCase):
    @patch("klatchat_utils.configuration.Configuration")
    def test_valid_klat_configuration(self, config):
        config.return_value = mock_valid_configuration
        klat_config = MockConfig()
        self.assertEqual(klat_config.config_data,
                         mock_valid_configuration[klat_config.config_key],
                         klat_config.config_data)

        # TODO: Test add_new_config_properties

    @patch("klatchat_utils.configuration.Configuration")
    def test_invalid_klat_configuration(self, config):
        # Missing module config
        config.return_value = mock_missing_top_key
        with self.assertRaises(MalformedConfigurationException):
            MockConfig()

        # Incomplete module config
        config.return_value = mock_missing_sub_key
        with self.assertRaises(MalformedConfigurationException):
            MockConfig()
