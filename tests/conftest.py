"""
Fixtures for roedoe testing.

These fixtures involve the creation of temporary trees in the filesystem,
whose structure is denoted by a "tree specification", which is simply a
nested dictionary with the following properties:

    - Keys are strings, which will become names of files, links,
    or directories in the temp tree created in the filesystem.

    - A value of None means "create a file here"; specifically, an empty file
    will be created.

    - A value of type Link represents a relative soft link to some
    destination specified relatively.

    - A value of type LinkWithinTree represents an absolute soft link to some
    destination specified relative to the root of the created tree.

    - A value of type dict represents a subdirectory, whose structure is
    specified by interpreting the value itself as a tree specification.
"""

import functools
import os
import shutil
import tempfile


import attr
import pytest


TESTBASE = '/tmp'


@attr.s
class Link(object):
    """Representing a soft link in a test tree."""
    src = attr.ib()


@attr.s
class LinkWithinTree(object):
    """
    Representing an absolute soft link specified relatively within a test tree.
    """
    src = attr.ib()


@pytest.fixture(scope='session')
def basic(request):
    """A very basic tree with not much drama."""
    spec = {
        'a': {
            'a': {
                'd': None,
                'e': None,
            },
            'b': None,
            'f': None,
            'g': {
            },
        },
        'h': {
            'a': {
                'i': None,
            }
        },
        'j': {
            'a': None,
        },
    }
    return spec, temp_tree_for_fixture(spec, request)


@pytest.fixture(scope='session')
def mutual_empty(request):
    """Two mutually recursive trees with no actual files."""
    spec = {
        'a': {
            'b': {
                'c': LinkWithinTree('d'),
            },
        },
        'd': {
            'e': {
                'f': LinkWithinTree('a'),
            },
        },
    }
    return spec, temp_tree_for_fixture(spec, request)


@pytest.fixture(scope='session')
def mutual_one_file(request):
    """Like mutual_empty but with a file in the second tree."""
    spec = {
        'a': {
            'b': {
                'c': LinkWithinTree('d'),
            },
        },
        'd': {
            'e': {
                'f': LinkWithinTree('a'),
                'g': None,
            },
        },
    }
    return spec, temp_tree_for_fixture(spec, request)


@pytest.fixture(scope='session')
def triple_linked(request):
    """
    Three trees with links across them (specified absolute and relative).
    """
    spec = {
        'a': {
            'b': {
                'c': LinkWithinTree('d'),
            },
        },
        'd': {
            'e': {
                'f': Link('../../g'),
            },
        },
        'g': {
            'h': {
                'i': None,
            },
        },
    }
    return spec, temp_tree_for_fixture(spec, request)


@pytest.fixture(scope='session')
def with_suffixes(request):
    """A tree with filenames with suffixes (for testing filtering)."""
    spec = {
        'foo': {
            'bar.md': None,
            'moo': {
                'BAR.MD': None,
                'thing': None,
                'zoo': {
                    'BAR.md': None,
                    'BAR.RST': None,
                },
            },
        },
        'fred': Link('zoom'),
        'zoom': {
            'blah.txt': None,
            'klang.rst': None,
            'wuub': None,
        }
    }
    return spec, temp_tree_for_fixture(spec, request)


# Helpers

def temp_tree_for_fixture(tree_spec, request):
    """
    Create a temporary test tree for a fixture given some spec.

    :param tree_spec: a tree specification, as described in this module's
    docstring.
    :param request: pytest.FixtureRequest object for fixture being set up.

    :return tmpdir: path to temp dir containing tree.
    """
    tmpdir = tempfile.mkdtemp(prefix='rd.', dir=TESTBASE)
    create_tree(tmpdir, tree_spec)
    request.addfinalizer(functools.partial(shutil.rmtree, tmpdir))
    return tmpdir


def create_tree(root, tree_spec):

    """
    Create a tree from some spec at some root.

    :param root: path to root of tree; probably a temporary directory of some
    sort.
    :param tree_spec: a tree specification, as described in this module's
    docstring.
    """

    def _create_tree(subtree_root, subtree):
        for k, v in subtree.items():
            path = os.path.join(subtree_root, k)
            if v is None:
                # Touch file
                open(path, 'a').close()
            elif isinstance(v, dict):
                os.mkdir(path)
                _create_tree(path, v)
            elif isinstance(v, LinkWithinTree):
                os.symlink(os.path.realpath(os.path.join(root, v.src)), path)
            elif isinstance(v, Link):
                os.symlink(v.src, path)
            else:
                raise ValueError((k, v))

    _create_tree(root, tree_spec)
