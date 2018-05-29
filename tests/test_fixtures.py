"""
Tests that fixtures actually set up files as we'd expect.
"""

import os


def test_basic(basic):
    _, tmpdir = basic
    assert_isdir_(tmpdir, '')
    assert_isdir_(tmpdir, 'a')
    assert_isfile(tmpdir, 'a/b')
    assert_isdir_(tmpdir, 'a/a')
    assert_isfile(tmpdir, 'a/a/d')
    assert_isfile(tmpdir, 'a/a/e')
    assert_isfile(tmpdir, 'a/f')
    assert_isdir_(tmpdir, 'a/g')
    assert_isdir_(tmpdir, 'h')
    assert_isdir_(tmpdir, 'h/a')
    assert_isfile(tmpdir, 'h/a/i')
    assert_isdir_(tmpdir, 'j')
    assert_isfile(tmpdir, 'j/a')


def test_mutual_empty(mutual_empty):
    _, tmpdir = mutual_empty
    assert_isdir_(tmpdir, '')
    assert_isdir_(tmpdir, 'a')
    assert_isdir_(tmpdir, 'a/b')
    assert_islink(tmpdir, 'a/b/c', os.path.join(tmpdir, 'd'))
    assert_isdir_(tmpdir, 'd')
    assert_isdir_(tmpdir, 'd/e')
    assert_islink(tmpdir, 'd/e/f', os.path.join(tmpdir, 'a'))


def test_mutual_one_file(mutual_one_file):
    _, tmpdir = mutual_one_file
    assert_isdir_(tmpdir, '')
    assert_isdir_(tmpdir, 'a')
    assert_isdir_(tmpdir, 'a/b')
    assert_islink(tmpdir, 'a/b/c', os.path.join(tmpdir, 'd'))
    assert_isdir_(tmpdir, 'd')
    assert_isdir_(tmpdir, 'd/e')
    assert_islink(tmpdir, 'd/e/f', os.path.join(tmpdir, 'a'))
    assert_isfile(tmpdir, 'd/e/g')


def test_triple_linked(triple_linked):
    _, tmpdir = triple_linked
    assert_isdir_(tmpdir, '')
    assert_isdir_(tmpdir, 'a')
    assert_isdir_(tmpdir, 'a/b')
    assert_islink(tmpdir, 'a/b/c', os.path.join(tmpdir, 'd'))
    assert_isdir_(tmpdir, 'd')
    assert_isdir_(tmpdir, 'd/e')
    assert_islink(tmpdir, 'd/e/f', os.path.join(tmpdir, 'g'))
    assert_isdir_(tmpdir, 'g')
    assert_isdir_(tmpdir, 'g/h')
    assert_isfile(tmpdir, 'g/h/i')


def test_foobar(with_suffixes):
    _, tmpdir = with_suffixes
    assert_isdir_(tmpdir, '')
    assert_isdir_(tmpdir, 'foo')
    assert_isfile(tmpdir, 'foo/bar.md')
    assert_isdir_(tmpdir, 'foo/moo')
    assert_isfile(tmpdir, 'foo/moo/BAR.MD')
    assert_isfile(tmpdir, 'foo/moo/thing')
    assert_isdir_(tmpdir, 'foo/moo/zoo')
    assert_isfile(tmpdir, 'foo/moo/zoo/BAR.md')
    assert_isfile(tmpdir, 'foo/moo/zoo/BAR.RST')
    assert_islink(tmpdir, 'fred', os.path.join(tmpdir, 'zoom'))
    assert_isdir_(tmpdir, 'zoom')
    assert_isfile(tmpdir, 'zoom/blah.txt')
    assert_isfile(tmpdir, 'zoom/klang.rst')


# Helpers

def assert_isdir_(root, path):
    """Assert some fs path is a directory."""
    path = os.path.join(root, *(path.split('/')))
    assert os.path.isdir(path), 'Dir not found: {}'.format(path)


def assert_isfile(root, path):
    """Assert some fs path is a regular file."""
    path = os.path.join(root, *(path.split('/')))
    assert os.path.isfile(path), 'File not found: {}'.format(path)


def assert_islink(root, path, src):
    """
    Assert some fs path is a symlink to the specified absolute destination.
    """
    path = os.path.join(root, *(path.split('/')))
    assert os.path.islink(path), 'Link not found: {}'.format(path)
    resolved_src = os.path.realpath(path)
    desired = os.path.realpath(os.path.join(os.path.dirname(path), src))
    assert resolved_src == desired, (
        'Link from {} points to {} not as expected {}'.format(
            path, resolved_src, desired))
