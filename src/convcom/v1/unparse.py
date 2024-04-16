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

from convcom.v1.types import ConventionalCommit


def unparse_commit(conventional_commit: ConventionalCommit) -> str:
    """Unparses a `ConventionalCommit` object.

    Args:
      conventional_commit: The `ConventionalCommit` object.

    Returns:
      A commit string.
    """

    type: Final[str] = conventional_commit.header.type
    scope: Final[str | None] = conventional_commit.header.scope
    is_breaking_change: Final[bool] = conventional_commit.header.is_breaking_change
    description: Final[str] = conventional_commit.header.description

    commit: str = type
    if not scope is None:
        commit += f"({scope})"
    if is_breaking_change:
        commit += "!"
    commit += f": {description}"

    if not conventional_commit.body is None:
        paragraphs: Final[list[str]] = conventional_commit.body.paragraphs

        commit += "\n\n"
        commit += "\n\n".join(paragraphs)

    if not conventional_commit.footer is None:
        trailers: Final[dict[str, list[str]]] = conventional_commit.footer.trailers

        commit += "\n"

        token: str
        strings: list[str]
        for token, strings in trailers.items():
            string: str
            for string in strings:
                commit += f"\n{token}: {string}"

    return commit
