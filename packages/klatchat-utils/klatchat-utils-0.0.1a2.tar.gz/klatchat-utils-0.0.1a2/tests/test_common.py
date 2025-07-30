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

from io import BytesIO
from unittest import TestCase


class TestCommon(TestCase):
    def test_generate_uuid(self):
        from klatchat_utils.common import generate_uuid

        # Default behavior
        self.assertIsInstance(generate_uuid(), str)

        # Maximum len
        long_uuid = generate_uuid(32)
        self.assertIsInstance(long_uuid, str)
        self.assertEqual(len(long_uuid), 32)

        # Minimum len
        long_uuid = generate_uuid(1)
        self.assertIsInstance(long_uuid, str)
        self.assertEqual(len(long_uuid), 1)

        # Error minimum len
        with self.assertRaises(ValueError):
            generate_uuid(0)

        # Error maximum len
        with self.assertRaises(ValueError):
            generate_uuid(33)

    def test_get_hash(self):
        from klatchat_utils.common import get_hash
        test_string = "test"

        # Default behavior
        self.assertIsInstance(get_hash(test_string), str)

        # Valid hash
        self.assertIsInstance(get_hash(test_string, algo="sha1"), str)

        # Invalid hash
        with self.assertRaises(ValueError):
            get_hash(test_string, algo="some_invalid_hash")

        # TODO: Test encoding

    def test_buffer_to_base64(self):
        from klatchat_utils.common import buffer_to_base64
        from klatchat_utils.common import base64_to_buffer

        test_bytes = BytesIO(b"test")
        encoded = buffer_to_base64(test_bytes)
        self.assertIsInstance(encoded, str)
        self.assertEqual(base64_to_buffer(encoded).getvalue(),
                         test_bytes.getvalue())

        # TODO: Test edge/error cases
