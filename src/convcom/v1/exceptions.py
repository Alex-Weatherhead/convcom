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

from typing import Final


class CommitParsingError(Exception):

    def __init__(self, commit: str) -> None:
        self._commit: Final[str] = commit

    def __str__(self) -> str:
        indented_commit: Final[str] = "\t" + self._commit.replace("\n", "\n\t")
        return f"Unable to parse commit:\n\n{indented_commit}\n\nPlease refer to https://www.conventionalcommits.org/en/v1.0.0/ for details on the Conventional Commit specification."
