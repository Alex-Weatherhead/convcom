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
from re import finditer, match, Match, search
from typing import Final, Iterator

from convcom.v1.types import Body, ConventionalCommit, Footer, Header
from convcom.v1.exceptions import CommitParsingError

TOKEN_GROUP: Final[str] = "token"
STRING_GROUP: Final[str] = "string"
# 'BREAKING-CHANGE' and 'BREAKING CHANGE' must be followed by a colon.
TOKEN_SUB_PATTERN: Final[str] = (
    rf"((?!BREAKING-CHANGE)[a-zA-Z-]+ #|(BREAKING CHANGE|[a-zA-Z-]+): )"
)
TRAILER_PATTERN: Final[str] = (
    rf"\n(?P<{TOKEN_GROUP}>{TOKEN_SUB_PATTERN})(?P<{STRING_GROUP}>((?!\n{TOKEN_SUB_PATTERN})(.|\n))*((?!\n{TOKEN_SUB_PATTERN}).)+)"
)

PARAGRAPH_GROUP: Final[str] = "paragraph"
BODY_PATTERN: Final[str] = rf"\n\n(?P<{PARAGRAPH_GROUP}>((?!{TOKEN_SUB_PATTERN}).)+)"

TYPE_GROUP: Final[str] = "type"
SCOPE_GROUP: Final[str] = "scope"
BREAKING_CHANGE_INDICATOR_GROUP: Final[str] = "breaking_change_indicator"
DESCRIPTION_GROUP: Final[str] = "description"
HEADER_PATTERN: Final[str] = (
    rf"^(?P<{TYPE_GROUP}>[a-zA-Z]*)(\((?P<{SCOPE_GROUP}>[a-zA-Z]*)\))?(?P<{BREAKING_CHANGE_INDICATOR_GROUP}>!)?: (?P<{DESCRIPTION_GROUP}>.*)$"
)


def parse_commit(commit: str) -> ConventionalCommit:
    """Parses a conventional commit.

    Args:
      commit: The conventional commit.

    Returns:
      A new `ConventionalCommit` object.

    Raises:
      CommitParsingError: if the commit string does adhere to the
        conventional commit specification.
    """

    header: Header | None = None
    body: Body | None = None
    footer: Footer | None = None

    splits: Final[list[str]] = commit.split("\n", 1)

    header = _parse_header(splits[0])
    if header is None:
        raise CommitParsingError(commit)

    if len(splits) > 1:
        body_and_footer: str = f"\n{splits[1]}"

        index_and_footer: tuple[int, Footer] | None = _parse_footer(body_and_footer)
        if not index_and_footer is None:
            index: int
            index, footer = index_and_footer
            if index > 0:
                body = _parse_body(body_and_footer[:index])
                if body is None:
                    raise CommitParsingError(commit)
        else:
            body = _parse_body(body_and_footer)
            if body is None:
                raise CommitParsingError(commit)

    return ConventionalCommit(header=header, body=body, footer=footer)


def _parse_header(header: str) -> Header | None:
    """Parses the header of a conventional commit.

    Args:
      header: The header of the conventional commit.

    Returns:
      `None` if `header` does not conform to the conventional
        commit specification; otherwise, a `Header` object.
    """

    header_pattern_match: Match[str] | None = match(HEADER_PATTERN, header)

    if header_pattern_match is None:
        return None

    return Header(
        type=header_pattern_match.group(TYPE_GROUP),
        scope=header_pattern_match.group(SCOPE_GROUP),
        is_breaking_change=header_pattern_match.group(BREAKING_CHANGE_INDICATOR_GROUP)
        == "!",  # fmt: skip
        description=header_pattern_match.group(DESCRIPTION_GROUP),
    )


def _parse_body(body: str) -> Body | None:
    """Parses the body of a conventional commit.

    Args:
      body: The body of the conventional commit.

    Returns:
      `None` if the commit has no body; otherwise, a `Body` object.
    """

    paragraphs: Final[list[str]] = []

    paragraph_start_index: int
    paragraph_end_index: int
    current_index: int = 0

    body_pattern_match: Match[str]
    body_pattern_matches_iterator: Final[Iterator[Match[str]]] = finditer(
        BODY_PATTERN, body
    )
    for body_pattern_match in body_pattern_matches_iterator:
        paragraph_start_index, paragraph_end_index = body_pattern_match.span()

        # Ensure that the next paragraph starts immediately after the preceding one
        if paragraph_start_index != current_index:
            break

        paragraphs.append(body_pattern_match.group(PARAGRAPH_GROUP))

        current_index = paragraph_end_index

    if len(paragraphs) > 0 and current_index == len(body):
        return Body(paragraphs=paragraphs)

    return None


def _parse_footer(body_and_footer: str) -> tuple[int, Footer] | None:
    """Parses the footer of a conventional commit.

    In order to identify where the footer of the commit actually begins,
    this method searches for the first instance of a trailer that occurs
    after a blank line.

    Args:
      body_and_footer: The body and footer of the conventional commit.

    Returns:
      `None` if the commit has no footer; otherwise, a tuple consisting of the
        index in `body_and_footer` at which the footer starts as well as a `Footer`
        object.
    """

    trailers: Final[OrderedDict[str, list[str]]] = OrderedDict()

    footer_start_index: int = -1
    remaining_footer_length: int = -1
    current_index: int = 0

    # The first trailer must be separated from the body by one blank line.
    trailer_pattern_match: Match[str] | None = search(
        "\n" + TRAILER_PATTERN, body_and_footer
    )
    if not trailer_pattern_match is None:
        trailer_start_index: int
        trailer_end_index: int
        footer_start_index, trailer_end_index = trailer_pattern_match.span()

        remaining_footer: str = body_and_footer[trailer_end_index:]
        remaining_footer_length = len(remaining_footer)

        _add_trailer(trailer_pattern_match, trailers)

        trailer_pattern_matches_iterator: Final[Iterator[Match[str]]] = finditer(
            TRAILER_PATTERN, remaining_footer
        )
        for trailer_pattern_match in trailer_pattern_matches_iterator:
            trailer_start_index, trailer_end_index = trailer_pattern_match.span()

            # Ensure that the next footer starts immediately after the preceding one.
            if trailer_start_index != current_index:
                break

            _add_trailer(trailer_pattern_match, trailers)

            current_index = trailer_end_index

    if len(trailers) > 0 and current_index == remaining_footer_length:
        is_breaking_change: bool = (
            ("BREAKING CHANGE" in trailers) or 
            ("BREAKING-CHANGE" in trailers)
        )  # fmt: skip

        return (
            footer_start_index,
            Footer(
                trailers=trailers,
                is_breaking_change=is_breaking_change,
            ),
        )

    return None


def _add_trailer(
    trailer_pattern_match: Match, trailers: OrderedDict[str, list[str]]
) -> None:
    """Adds a new trailer to an ordered dictionary of trailers.

    Args:
        trailer_pattern_match: The regex pattern match of the trailer.
        trailers: The ordered dictionary of trailers to add to.
    """

    # Remove the ' #' or ': ' separator from the token.
    token: str = trailer_pattern_match.group(TOKEN_GROUP)[:-2]
    string: str = trailer_pattern_match.group(STRING_GROUP)

    if token in trailers:
        trailers[token].append(string)
    else:
        trailers[token] = [string]
