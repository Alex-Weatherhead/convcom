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

from textwrap import dedent

from convcom.v1.types import Body, ConventionalCommit, Footer, Header
from convcom.v1.unparse import unparse_commit

def test_unparse_on_commit():
    # Setup
    expected_commit: str = "feat: add a new feature!"

    # Act
    actual_commit: str = unparse_commit(
        ConventionalCommit(
            header=Header(
                type="feat",
                description="add a new feature!"
            )
        )
    )

    # Assert
    assert expected_commit == actual_commit

def test_unparse_on_commit_with_a_scope():
    # Setup
    expected_commit: str = "feat(website): add a new feature!"

    # Act
    actual_commit: str = unparse_commit(
        ConventionalCommit(
            header=Header(
                type="feat",
                scope="website",
                description="add a new feature!"
            )
        )
    )

    # Assert
    assert expected_commit == actual_commit

def test_unparse_on_commit_with_a_breaking_change_indicator():
    # Setup
    expected_commit: str = "feat!: add a new feature!"

    # Act
    actual_commit: str = unparse_commit(
        ConventionalCommit(
            header=Header(
                type="feat",
                is_breaking_change=True,
                description="add a new feature!"
            )
        )
    )

    # Assert
    assert expected_commit == actual_commit   

def test_unparse_on_commit_with_a_scope_and_a_breaking_change_indicator():
    # Setup
    expected_commit: str = "feat(website)!: add a new feature!"

    # Act
    actual_commit: str = unparse_commit(
        ConventionalCommit(
            header=Header(
                type="feat",
                scope="website",
                is_breaking_change=True,
                description="add a new feature!"
            )
        )
    )

    # Assert
    assert expected_commit == actual_commit

def test_unparse_on_commit_with_a_single_paragraph_in_body():
    # Setup
    expected_commit: str = dedent(
        """\
        feat: add a new feature!

        This is the first paragraph..."""
    )

    # Act
    actual_commit: str = unparse_commit(
        ConventionalCommit(
            header=Header(
                type="feat",
                description="add a new feature!"
            ),
            body=Body(
                paragraphs=[
                    "This is the first paragraph..."
                ]
            )
        )
    )

    # Assert
    assert expected_commit == actual_commit

def test_unparse_on_commit_with_multiple_paragraphs_in_body():
    # Setup
    expected_commit: str = dedent(
        """\
        feat: add a new feature!

        This is the first paragraph...

        This is the second paragraph..."""
    )

    # Act
    actual_commit: str = unparse_commit(
        ConventionalCommit(
            header=Header(
                type="feat",
                description="add a new feature!"
            ),
            body=Body(
                paragraphs=[
                    "This is the first paragraph...",
                    "This is the second paragraph..."
                ]
            )
        )
    )

    # Assert
    assert expected_commit == actual_commit

def test_unparse_on_commit_with_a_single_trailer_in_footer():
    # Setup
    expected_commit: str = dedent(
        """\
        feat: add a new feature!

        Refs: a4b9jg385"""
    )

    # Act
    actual_commit: str = unparse_commit(
        ConventionalCommit(
            header=Header(
                type="feat",
                description="add a new feature!"
            ),
            footer=Footer(
                trailers={
                    "Refs": ["a4b9jg385"]
                }
            )
        )
    )

    # Assert
    assert expected_commit == actual_commit

def test_unparse_on_commit_with_a_single_multiline_trailer_in_footer():
    # Setup
    expected_commit: str = dedent(
        """\
        feat: add a new feature!

        Refs: 
        \ta4b9jg385,
        \tmb7y8n1v5"""
    )

    # Act
    actual_commit: str = unparse_commit(
        ConventionalCommit(
            header=Header(
                type="feat",
                description="add a new feature!"
            ),
            footer=Footer(
                trailers={
                    "Refs": ["\n\ta4b9jg385,\n\tmb7y8n1v5"]
                }
            )
        )
    )

    # Assert
    assert expected_commit == actual_commit  

def test_unparse_on_commit_with_multiple_trailers_in_footer():
    # Setup
    expected_commit: str = dedent(
        """\
        feat: add a new feature!

        Refs: a4b9jg385
        PR: #1"""
    )

    # Act
    actual_commit: str = unparse_commit(
        ConventionalCommit(
            header=Header(
                type="feat",
                description="add a new feature!"
            ),
            footer=Footer(
                trailers={
                    "Refs": ["a4b9jg385"],
                    "PR": ["#1"]
                }
            )
        )
    )

    # Assert
    assert expected_commit == actual_commit

def test_unparse_on_commit_with_duplicate_trailers_in_footer():
    # Setup
    expected_commit: str = dedent(
        """\
        feat: add a new feature!

        Refs: a4b9jg385
        Refs: mb7y8n1v5"""
    )

    # Act
    actual_commit: str = unparse_commit(
        ConventionalCommit(
            header=Header(
                type="feat",
                description="add a new feature!"
            ),
            footer=Footer(
                trailers={
                    "Refs": ["a4b9jg385", "mb7y8n1v5"]
                }
            )
        )
    )

    # Assert
    assert expected_commit == actual_commit
