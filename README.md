# convcom

A simple pure-Python module for parsing [V1](https://www.conventionalcommits.org/en/v1.0.0/) of the conventional commits specification.

## Install

To install the latest release, run:

```shell
$ pip install convcom
```

To upgrade `convcom` to the latest version, add the `--upgrade` flag to the above command. 

## Quickstart

To get started, first open your Python interpreter:

```shell
$ python
```

Now, let's parse our first commit:

```python
>>> from convcom.v1.parse import parse_commit
>>> parse_commit('feat: my new feature!')
ConventionalCommit(header=Header(type='feat', description='my new feature!', scope=None, is_breaking_change=False), body=None, footer=None)
```

Next, let's do the same thing, but in reverse:

```python
>>> from convcom.v1.types import ConventionalCommit, Header
>>> from convcom.v1.unparse import unparse_commit
>>> unparse_commit(ConventionalCommit(header=Header(type='feat', description='my new feature!')))
'feat: my new feature!'
```

Ta-da! 🎉 You should now have all the tools you need to start working with conventional commits.

For more [advanced](#advanced) use-cases, keep reading.

## Advanced

### Adding a scope

A scope can be added to a header after the type:

```python
>>> from convcom.v1.parse import parse_commit
>>> parse_commit('feat(website): my new UI feature!')
ConventionalCommit(header=Header(type='feat', description='my new UI feature!', scope='website', is_breaking_change=False), body=None, footer=None)
```

### Adding a body

Paragraphs can be added to a body:

```python
>>> from convcom.v1.parse import parse_commit
>>> parse_commit('feat(website): my new UI feature!\n\nSome details...\n\nSome more details...')
ConventionalCommit(header=Header(type='feat', description='my new UI feature!', scope='website', is_breaking_change=False), body=Body(paragraphs=['Some details...', 'Some more details...']), footer=None)
```

### Adding a footer

Trailers can be added to a footer:

```python
>>> from convcom.v1.parse import parse_commit
>>> parse_commit('feat: my new feature!\n\nIssue: #1')
ConventionalCommit(header=Header(type='feat', description='my new feature!', scope=None, is_breaking_change=False), body=None, footer=Footer(trailers=OrderedDict({'Issue': ['#1']}), is_breaking_change=False))
```

A trailers token can also repeat multiple times within a footer:

```python
>>> from convcom.v1.parse import parse_commit
>>> parse_commit('feat: my new feature!\n\nIssue: #1\nIssue: #2')
ConventionalCommit(header=Header(type='feat', description='my new feature!', scope=None, is_breaking_change=False), body=None, footer=Footer(trailers=OrderedDict({'Issue': ['#1', '#2']}), is_breaking_change=False))
```

### Indicating a breaking change

Breaking changes can indicated using a '!' in the header:

```python
>>> from convcom.v1.parse import parse_commit
>>> parse_commit('feat!: my new breaking feature!')
ConventionalCommit(header=Header(type='feat', description='my new breaking feature!', scope=None, is_breaking_change=True), body=None, footer=None)
```

Breaking changes can also be indicated using a 'BREAKING CHANGE' or 'BREAKING-CHANGE' trailer in the footer:

```python
>>> from convcom.v1.parse import parse_commit
>>> parse_commit('feat: my new feature!\n\nBREAKING-CHANGE: This feature breaks things...')
ConventionalCommit(header=Header(type='feat', description='my new feature!', scope=None, is_breaking_change=False), body=None, footer=Footer(trailers=OrderedDict({'BREAKING-CHANGE': ['This feature breaks things...']}), is_breaking_change=True))
```

To simplify things, the `ConventionalCommit` class has a convenience method for checking if the commit is a breaking change:

```python
>>> from convcom.v1.parse import parse_commit
>>> parse_commit('feat!: my new breaking feature!').is_breaking_change()
True
>>> parse_commit('feat: my new feature!\n\nBREAKING-CHANGE: This feature breaks things...').is_breaking_change()
True
```
