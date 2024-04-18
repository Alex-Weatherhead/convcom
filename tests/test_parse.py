# This file is part of the convcom 
# Copyright (C) 2024  Alex Weatherhead
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations


from textwrap import dedent

import pytest

from convcom.v1.exceptions import CommitParsingError
from convcom.v1.parse import parse_commit
from convcom.v1.types import Body, ConventionalCommit, Footer, Header

# Positive tests

@pytest.mark.parametrize(
    "type",
    [
        "feat",
        "fix"
    ]
)
def test_parse_on_commit(type: str):
    # Setup
    expected_conventional_commit: ConventionalCommit = ConventionalCommit(
        header=Header(
            type=type,
            scope=None,
            is_breaking_change=False,
            description="lorem ipsum dolor sit amet"
        )
    )

    # Act
    actual_conventional_commit: ConventionalCommit = parse_commit(f"{type}: lorem ipsum dolor sit amet")

    # Assert
    assert expected_conventional_commit == actual_conventional_commit

@pytest.mark.parametrize(
    "type,scope",
    [
        ("feat", "website"),
        ("feat", "backend"),
        ("fix", "website"),
        ("fix", "backend")
    ]
)
def test_parse_on_commit_with_scope(type: str, scope: str):
    # Setup
    expected_conventional_commit: ConventionalCommit = ConventionalCommit(
        header=Header(
            type=type,
            scope=scope,
            description="lorem ipsum dolor sit amet"
        )
    )

    # Act
    actual_conventional_commit: ConventionalCommit = parse_commit(f"{type}({scope}): lorem ipsum dolor sit amet")

    # Assert
    assert expected_conventional_commit == actual_conventional_commit

@pytest.mark.parametrize(
    "type",
    [
        "feat",
        "fix"
    ]
)
def test_parse_on_commit_with_breaking_change_indicator(type: str):
    # Setup
    expected_conventional_commit: ConventionalCommit = ConventionalCommit(
        header=Header(
            type=type,
            is_breaking_change=True,
            description="lorem ipsum dolor sit amet"
        )
    )

    # Act
    actual_conventional_commit: ConventionalCommit = parse_commit(f"{type}!: lorem ipsum dolor sit amet")

    # Assert
    assert expected_conventional_commit == actual_conventional_commit

@pytest.mark.parametrize(
    "type,scope",
    [
        ("feat", "website"),
        ("feat", "backend"),
        ("fix", "website"),
        ("fix", "backend")
    ]
)
def test_parse_on_commit_with_scope_and_breaking_change_indicator(type: str, scope: str):
    # Setup
    expected_conventional_commit: ConventionalCommit = ConventionalCommit(
        header=Header(
            type=type,
            scope=scope,
            is_breaking_change=True,
            description="lorem ipsum dolor sit amet"
        )
    )

    # Act
    actual_conventional_commit: ConventionalCommit = parse_commit(f"{type}({scope})!: lorem ipsum dolor sit amet")

    # Assert
    assert expected_conventional_commit == actual_conventional_commit

def test_parse_on_commit_with_a_single_paragraph_in_body():
    # Setup
    expected_components: ConventionalCommit = ConventionalCommit(
        header=Header(
            type="feat",
            scope="website",
            description="add a new feature!"
        ),
        body=Body(
            paragraphs=[
                "Some details about this change..."
            ]
        )
    )
    
    # Act
    actual_components: ConventionalCommit = parse_commit(
        dedent(
            """\
            feat(website): add a new feature!
        
            Some details about this change..."""
        )
    )

    # Assert
    assert expected_components == actual_components
 
def test_parse_on_commit_with_multiple_paragraphs_in_body():
    # Setup
    expected_components: ConventionalCommit = ConventionalCommit(
        header=Header(
            type="feat",
            scope="website",
            description="add a new feature!"
        ),
        body=Body(
            paragraphs=[
                "Some details about this change...",
                "A few more details about this change..."
            ]
        )
    )
    
    # Act
    actual_components: ConventionalCommit = parse_commit(
        dedent(
            """\
            feat(website): add a new feature!
        
            Some details about this change...

            A few more details about this change..."""
        )
    )

    # Assert
    assert expected_components == actual_components

@pytest.mark.parametrize(
    "token,separator,string",
    [
        ("placeholder", ": ", "lorem ipsum dolor sit amet"),
        ("placeholder", " #", "lorem ipsum dolor sit amet"),
        ("pull-request", ": ", "id #123"),
        ("see-also", " #", "refs: a4b9jg385,0pql18nv6")
    ]
)
def test_parse_on_commit_with_a_single_non_breaking_change_trailer_in_footer(token: str, separator: str, string: str):
    # Setup
    expected_conventional_commit: ConventionalCommit = ConventionalCommit(
        header=Header(
            type="feat",
            description="add a new feature!"
        ),
        footer=Footer(
            trailers={
                token: [string]
            },
            is_breaking_change=False
        )
    )

    # Act
    actual_conventional_commit = parse_commit(
        dedent(
            f"""\
            feat: add a new feature!
        
            {token}{separator}{string}"""
        )
    )

    # Assert
    assert expected_conventional_commit == actual_conventional_commit

@pytest.mark.parametrize(
    "token",
    [
        "BREAKING CHANGE",
        "BREAKING-CHANGE"
    ]
)
def test_parse_on_commit_with_a_single_breaking_change_trailer_in_footer(token: str):
    # Setup
    expected_conventional_commit: ConventionalCommit = ConventionalCommit(
        header=Header(
            type="feat",
            description="add a new feature!"
        ),
        footer=Footer(
            trailers={
                token: ["lorem ipsum dolor sit amet"]
            },
            is_breaking_change=True
        )
    )

    # Act
    actual_conventional_commit: ConventionalCommit = parse_commit(
        dedent(
            f"""\
            feat: add a new feature!
        
            {token}: lorem ipsum dolor sit amet"""
        )
    )

    # Assert
    assert expected_conventional_commit == actual_conventional_commit

def test_parse_on_commit_with_duplicate_non_breaking_change_trailers_in_footer():
    # Setup
    expected_conventional_commit: ConventionalCommit = ConventionalCommit(
        header=Header(
            type="feat",
            description="add a new feature!"
        ),
        footer=Footer(
            trailers={
                "placeholder": ["lorem ipsum dolor sit amet", "consectetur adipiscing elit"]
            }
        )
    )

    # Act
    actual_conventional_commit: ConventionalCommit = parse_commit(
        dedent(
            f"""\
            feat: add a new feature!
        
            placeholder: lorem ipsum dolor sit amet
            placeholder #consectetur adipiscing elit"""
        )
    )

    # Assert
    assert expected_conventional_commit == actual_conventional_commit

def test_parse_on_commit_with_duplicate_breaking_change_trailers_in_footer():
    # Setup
    expected_conventional_commit: ConventionalCommit = ConventionalCommit(
        header=Header(
            type="feat",
            description="add a new feature!"
        ),
        footer=Footer(
            trailers={
                "BREAKING CHANGE": ["lorem ipsum dolor sit amet", "consectetur adipiscing elit"],
                "BREAKING-CHANGE": ["sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."]
            },
            is_breaking_change=True
        )
    )

    # Act
    actual_conventional_commit: ConventionalCommit = parse_commit(
        dedent(
            f"""\
            feat: add a new feature!
        
            BREAKING CHANGE: lorem ipsum dolor sit amet
            BREAKING CHANGE: consectetur adipiscing elit
            BREAKING-CHANGE: sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."""
        )
    )

    # Assert
    assert expected_conventional_commit == actual_conventional_commit

@pytest.mark.parametrize(
    "separator",
    [
        ": ",
        " #"
    ]
)
def test_parse_on_commit_with_a_single_multiline_trailer_in_footer(separator: str):
    # Setup
    expected_components: ConventionalCommit = ConventionalCommit(
        header=Header(type="feat", scope="website", description="add a new feature!", is_breaking_change=False),
        body=None,
        footer=Footer(trailers={"placeholder": ["lorem ipsum dolor sit amet\n\nconsectetur adipiscing elit"]}, is_breaking_change=False)
    )
    
    # Act
    actual_components: ConventionalCommit = parse_commit(
        dedent(
            f"""\
            feat(website): add a new feature!
        
            placeholder{separator}lorem ipsum dolor sit amet
            
            consectetur adipiscing elit"""
        )
    )

    # Assert
    assert expected_components == actual_components

def test_parse_on_commit_with_multiple_trailers_in_footer():
    # Setup
    expected_components: ConventionalCommit = ConventionalCommit(
        header=Header(
            type="feat",
            description="add a new feature!"
        ),
        footer=Footer(
            trailers={
                "Refs": ["a4b9jg385"],
                "Reviewed-by": ["Z"]
            }
        )
    )
    
    # Act
    actual_components: ConventionalCommit = parse_commit(
        dedent(
            """\
            feat: add a new feature!
        
            Refs: a4b9jg385
            Reviewed-by: Z"""
        )
    )

    # Assert
    assert expected_components == actual_components 

def test_parse_on_commit_with_multiple_multiline_trailer_in_footer():
    # Setup
    expected_components: ConventionalCommit = ConventionalCommit(
        header=Header(type="feat", scope="website", description="add a new feature!", is_breaking_change=False),
        body=None,
        footer=Footer(
            trailers={
                "placeholderA": ["lorem ipsum dolor sit amet\n\n\nconsectetur adipiscing elit"],
                "placeholderB": ["lorem ipsum dolor sit amet\nconsectetur adipiscing elit"]
            },
            is_breaking_change=False
        )
    )
    
    # Act
    actual_components: ConventionalCommit = parse_commit(
        dedent(
            """\
            feat(website): add a new feature!
        
            placeholderA: lorem ipsum dolor sit amet
            

            consectetur adipiscing elit
            placeholderB: lorem ipsum dolor sit amet
            consectetur adipiscing elit"""
        )
    )

    # Assert
    assert expected_components == actual_components

def test_parse_on_commit_with_multiple_paragraphs_in_body_and_a_single_trailer_in_footer():
    # Setup
    expected_components: ConventionalCommit = ConventionalCommit(
        header=Header(
            type="feat",
            scope="website",
            description="add a new feature!"
        ),
        body=Body(
            paragraphs=[
                "Some details about this change...",
                "A few more details about this change..."
            ]
        ),
        footer=Footer(
            trailers={
                "Refs": ["a4b9jg385"]
            }
        )
    )
    
    # Act
    actual_components: ConventionalCommit = parse_commit(
        dedent(
            """\
            feat(website): add a new feature!
        
            Some details about this change...

            A few more details about this change...
            
            Refs: a4b9jg385"""
        )
    )

    # Assert
    assert expected_components == actual_components

def test_parse_on_commit_with_multiple_paragraphs_in_body_and_multiple_trailers_in_footer():
    # Setup
    expected_components: ConventionalCommit = ConventionalCommit(
        header=Header(
            type="fix",
            description="prevent racing of requests"
        ),
        body=Body(
            paragraphs=[
                "Introduce a request id and a reference to latest request. Dismiss incoming responses other than from latest request.",
                "Remove timeouts which were used to mitigate the racing issue but are obsolete now."
            ]
        ),
        footer=Footer(
            trailers={
                "Reviewed-by": ["Z"],
                "Refs": ["#123"]
            }
        )
    ) 

    # Act
    actual_components: ConventionalCommit = parse_commit(
        dedent(
            """\
            fix: prevent racing of requests

            Introduce a request id and a reference to latest request. Dismiss incoming responses other than from latest request.

            Remove timeouts which were used to mitigate the racing issue but are obsolete now.

            Reviewed-by: Z
            Refs: #123"""
        )
    )

    # Assert
    assert expected_components == actual_components

def test_parse_on_commit_with_a_breaking_change_indicator_and_a_breaking_change_trailer_in_footer():
    # Setup
    expected_components: ConventionalCommit = ConventionalCommit(
        header=Header(
            type="chore",
            description="drop support for Node 6",
            is_breaking_change=True
        ),
        footer=Footer(
            trailers={
                "BREAKING CHANGE": ["use JavaScript features not available in Node 6."]
            },
            is_breaking_change=True
        )
    ) 

    # Act
    actual_components: ConventionalCommit = parse_commit(
        dedent(
            """\
            chore!: drop support for Node 6

            BREAKING CHANGE: use JavaScript features not available in Node 6."""
        )
    )

    # Assert
    assert expected_components == actual_components

# Negative tests

def test_parse_raises_parsing_error_when_the_commit_message_is_empty():
    with pytest.raises(CommitParsingError):
        parse_commit("")

def test_parse_raises_parsing_error_when_there_is_no_header():
    with pytest.raises(CommitParsingError):
        parse_commit(
            dedent(
                """\
                Introduce a request id and a reference to latest request. Dismiss incoming responses other than from latest request.

                Remove timeouts which were used to mitigate the racing issue but are obsolete now.

                Reviewed-by: Z
                Refs: #123"""
            )
        )

@pytest.mark.parametrize(
    "commit",
    [
        dedent(
            """\
            feat(website): add a new feature!
        
            Some details about this change...
            A few more details about this change...
            
            Refs: a4b9jg385"""
        ),
        dedent(
            """\
            feat(website): add a new feature!
        
            Some details about this change...


            A few more details about this change...
            
            Refs: a4b9jg385"""
        ),
    ]
)
def test_parse_raises_parsing_error_when_paragraphs_are_not_separated_by_exactly_one_blank_line(commit: str):
    # Assert
    with pytest.raises(CommitParsingError):
        # Act
        parse_commit(commit)

@pytest.mark.parametrize(
    "footer",
    [
        "lorem ipsum dolor sit amet\nplaceholder: consectetur adipiscing elit",
        "BREAKING-CHANGE: lorem ipsum dolor sit amet\nplaceholder: ",
        "BREAKING CHANGE #lorem ipsum dolor sit amet",
        "BREAKING-CHANGE #lorem ipsum dolor sit amet"
    ]
)
def test_parse_on_commit_with_invalid_footer(footer: str):
    # Assert
    with pytest.raises(CommitParsingError):
        # Act
        parse_commit(
            dedent(
                f"""\
                feat: add a new feature!

                {footer}"""
            )
        )
