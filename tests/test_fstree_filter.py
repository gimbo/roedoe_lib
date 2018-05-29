"""
Tests of base.FSTree.filter()
"""

import re


from roedoe_lib import FSTree


def test_filter_empty(basic):
    """Test an empty filter list."""
    _, tmpdir = basic
    tree = FSTree.at_path(tmpdir, {tmpdir})
    filtered = tree.filter([])
    assert filtered == FSTree({
        'a': FSTree({
            'b': None,
            'a': FSTree({
                'd': None,
                'e': None,
            }),
            'f': None,
        }),
        'h': FSTree({
            'a': FSTree({
                'i': None,
            }),
        }),
        'j': FSTree({
            'a': None,
        }),
    })


def test_filter_one(basic):
    """
    Test using a single filter.

    This test keeps matching files (but not matching directories),
    and that folders which are empty after filtering after filtered too.

    """
    _, tmpdir = basic
    tree = FSTree.at_path(tmpdir, {tmpdir})
    filtered = tree.filter([re.compile('.*a$')])
    assert filtered == FSTree({
        'j': FSTree({
            'a': None,
        }),
    })


def test_filter_many(basic):
    """
    Test using multiple filters.
    """
    _, tmpdir = basic
    tree = FSTree.at_path(tmpdir, {tmpdir})
    filtered = tree.filter(
        [re.compile(p) for p in ('.*a$', '.*(d|i)$', '.*e$')]
    )
    assert filtered == FSTree({
        'a': FSTree({
            'a': FSTree({
                'd': None,
                'e': None,
            }),
        }),
        'h': FSTree({
            'a': FSTree({
                'i': None,
            }),
        }),
        'j': FSTree({
            'a': None,
        }),
    })


def test_filter_suffix_md(with_suffixes):
    """
    Test filtering on *.md
    """
    _, tmpdir = with_suffixes
    tree = FSTree.at_path(tmpdir, {tmpdir})
    filtered = tree.filter([re.compile(r'.*\.md$')])
    assert filtered == FSTree({
        'foo': FSTree({
            'bar.md': None,
            'moo': FSTree({
                'zoo': FSTree({
                    'BAR.md': None,
                }),
            }),
        }),
    })


def test_filter_suffix_md_case_insens(with_suffixes):
    """
    Case insensitive version of test_filter_suffix_md
    """
    _, tmpdir = with_suffixes
    tree = FSTree.at_path(tmpdir, {tmpdir})
    md_insens = re.compile(r'.*\.md$', re.IGNORECASE)
    filtered = tree.filter([md_insens])
    assert filtered == FSTree({
        'foo': FSTree({
            'bar.md': None,
            'moo': FSTree({
                'BAR.MD': None,
                'zoo': FSTree({
                    'BAR.md': None,
                }),
            }),
        }),
    })


def test_filter_suffices_case_insens(with_suffixes):
    """
    Test the kind of filter we're really going to want to do.
    """
    _, tmpdir = with_suffixes
    tree = FSTree.at_path(tmpdir, {tmpdir})
    md_insens = re.compile(r'.*\.md$', re.IGNORECASE)
    rst_insens = re.compile(r'.*\.rst$', re.IGNORECASE)
    filtered = tree.filter([md_insens, rst_insens])
    assert filtered == FSTree({
        'foo': FSTree({
            'bar.md': None,
            'moo': FSTree({
                'BAR.MD': None,
                'zoo': FSTree({
                    'BAR.md': None,
                    'BAR.RST': None,
                }),
            }),
        }),
        'fred': FSTree({
            'klang.rst': None
        }),
    })


def test_filter_on_path(with_suffixes):
    """
    Test that filters can consider paths or path fragments.
    """
    _, tmpdir = with_suffixes
    tree = FSTree.at_path(tmpdir, {tmpdir})
    # A pattern specifying a full path to a file
    full = re.compile('^foo/moo/zoo/BAR.md$')
    # A pattern specifying a file prefix, i.e. a path to a directory.
    prefix = re.compile('^fred.*$')
    filtered = tree.filter([full, prefix])
    assert filtered == FSTree({
        'foo': FSTree({
            'moo': FSTree({
                'zoo': FSTree({
                    'BAR.md': None,
                }),
            }),
        }),
        'fred': FSTree({
            'blah.txt': None,
            'klang.rst': None,
            'wuub': None,
        }),
    })


def test_filter_dir_path_link_resolved(with_suffixes):
    """
    Test that matching vs a folder we linked to doesn't work.
    """
    _, tmpdir = with_suffixes
    tree = FSTree.at_path(tmpdir, {tmpdir})
    # Here zoom is not in our tree at all (as fred links to it); even though
    # it's part of the absolute name of some files, we're only matching vs
    # names in the tree, from which this name is pruned because fred already
    # got there.
    prefix = re.compile('^.*zoom.*$')
    filtered = tree.filter([prefix])
    assert filtered == FSTree({})
