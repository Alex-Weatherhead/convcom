# Copyright 2024 Alex Weatherhead
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

from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class Header:
    type: str
    description: str
    scope: str | None = None
    is_breaking_change: bool = False


@dataclass
class Body:
    paragraphs: list[str]


@dataclass
class Footer:
    trailers: OrderedDict[str, list[str]]
    is_breaking_change: bool = False


@dataclass
class ConventionalCommit:
    header: Header
    body: Body | None = None
    footer: Footer | None = None

    def is_breaking_change(self) -> bool:
        if self.header.is_breaking_change:
            return True
        elif not self.footer is None and self.footer.is_breaking_change:
            return True
        
        return False
