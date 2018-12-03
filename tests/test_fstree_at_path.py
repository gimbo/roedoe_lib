"""
Tests of FSTree.at_path() class method.
"""

import os

from roedoe_lib import FSTree, ignore


def test_basic(basic):
    """Test basic tree with not much drama."""
    _, tmpdir = basic
    tree = FSTree.at_path(tmpdir, {tmpdir})
    # Note no entry for 'a/g' - it's an empty folder
    jib = FSTree({
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

    assert tree == jib


def test_basic_subtree(basic):
    """Test subtree of basic tree with not much drama."""
    _, tmpdir = basic
    root = os.path.join(tmpdir, 'a')
    tree = FSTree.at_path(root, {root})
    # Note no entry for 'a/g' - it's an empty folder
    assert tree == FSTree({
        'b': None,
        'a': FSTree({
            'd': None,
            'e': None,
        }),
        'f': None,
    })


def test_basic_ignore_file_and_dir(basic):
    """Test ignoring some name used for file and directory."""
    _, tmpdir = basic
    tree = FSTree.at_path(tmpdir, {tmpdir}, ignore('a'))
    # Everything disappears
    assert tree == FSTree({})


def test_basic_ignore_several(basic):
    """Test ignoring several names."""
    _, tmpdir = basic
    tree = FSTree.at_path(tmpdir, {tmpdir}, ignore('b', 'h', 'j'))
    assert tree == FSTree({
        'a': FSTree({
            'a': FSTree({
                'd': None,
                'e': None,
            }),
            'f': None,
        }),
    })


def test_basic_ignore_dir(basic):
    """Test ignoring some directory (which appears twice)."""
    _, tmpdir = basic
    tree = FSTree.at_path(tmpdir, {tmpdir}, ignore('a/'))
    # Causes 'h' to go too since it's now empty
    assert tree == FSTree({
        'j': FSTree({
            'a': None,
        }),
    })


def test_basic_ignore_top_level_dir(basic):
    """Test ignoring some directory at the top level only."""
    _, tmpdir = basic
    tree = FSTree.at_path(tmpdir, {tmpdir}, ignore('/a/'))
    assert tree == FSTree({
        'h': FSTree({
            'a': FSTree({
                'i': None,
            })
        }),
        'j': FSTree({
            'a': None,
        }),
    })


def test_basic_ignore_tree_being_walked(basic):
    """Test ignoring the whole tree we're walking."""
    _, tmpdir = basic
    tree = FSTree.at_path(os.path.join(tmpdir, 'h'), {tmpdir}, ignore('h'))
    # Everything disappears
    assert tree == FSTree({})


# Tests vs mutually recursive linked trees; these should resolve cycles
# lexicographically, and respect tree restrictions.

def test_mutual_empty(mutual_empty):
    """Test two mutually recursive linked trees with no files."""
    _, tmpdir = mutual_empty
    tree = FSTree.at_path(os.path.join(tmpdir, 'a'), {tmpdir})
    assert tree == FSTree({})


def test_mutual_one_file_no_roots(mutual_one_file):
    """
    Test two mutually recursive linked trees with one file, with no valid roots.
    """
    _, tmpdir = mutual_one_file
    tree = FSTree.at_path(os.path.join(tmpdir, 'a'), set())
    assert tree == FSTree({})


def test_mutual_one_file_first_root_valid(mutual_one_file):
    """
    Test two mutually recursive linked trees with one file, where the tree
    the file is actually in is not a valid root.
    """
    _, tmpdir = mutual_one_file
    root = os.path.join(tmpdir, 'a')
    tree = FSTree.at_path(root, {root})
    assert tree == FSTree({})


def test_mutual_one_file_second_root_valid(mutual_one_file):
    """
    Test two mutually recursive linked trees with one file, where the tree we
    ask to query is not a valid root.
    """
    _, tmpdir = mutual_one_file
    root = os.path.join(tmpdir, 'a')
    other = os.path.join(tmpdir, 'd')
    tree = FSTree.at_path(root, {other})
    assert tree == FSTree({})


def test_mutual_one_file_both_valid_roots(mutual_one_file):
    """
    Test two mutually recursive linked trees with one file, where both trees
    are valid roots.
    """
    _, tmpdir = mutual_one_file
    root = os.path.join(tmpdir, 'a')
    other = os.path.join(tmpdir, 'd')
    tree = FSTree.at_path(root, {root, other})
    assert tree == FSTree({
        'b': FSTree({
            'c': FSTree({
                'e': FSTree({
                    'g': None,
                }),
            }),
        }),
    })


def test_mutual_one_file_parent_valid_root(mutual_one_file):
    """
    Test two mutually recursive linked trees with one file, where the parent
    is valid.
    """
    _, tmpdir = mutual_one_file
    root = os.path.join(tmpdir, 'a')
    tree = FSTree.at_path(root, {tmpdir})
    # Same result as before: valid parent implies valid children
    assert tree == FSTree({
        'b': FSTree({
            'c': FSTree({
                'e': FSTree({
                    'g': None,
                }),
            }),
        }),
    })


def test_mutual_one_file_parent_valid_root_start_root(mutual_one_file):
    """
    Test two mutually recursive linked trees with one file, where the parent
    is valid, starting at the parent.
    """
    _, tmpdir = mutual_one_file
    tree = FSTree.at_path(tmpdir, {tmpdir})
    # Same result as before, but with the extra layer of 'a'; no top-level
    # 'd' folder because we already found it while recursing into 'a'.
    assert tree == FSTree({
        'a': FSTree({
            'b': FSTree({
                'c': FSTree({
                    'e': FSTree({
                        'g': None,
                    }),
                }),
            }),
        }),
    })


def test_triple_linked_parent_valid(triple_linked):
    """
    Test linking across three trees, where their parent is a valid root.
    """
    _, tmpdir = triple_linked
    first = os.path.join(tmpdir, 'a')
    tree = FSTree.at_path(first, {tmpdir})
    assert tree == FSTree({
        'b': FSTree({
            'c': FSTree({
                'e': FSTree({
                    'f': FSTree({
                        'h': FSTree({
                            'i': None,
                        }),
                    }),
                }),
            }),
        }),
    })


def test_triple_linked_all_valid(triple_linked):
    """
    Test linking across three trees, where all three are valid roots.
    """
    _, tmpdir = triple_linked
    first = os.path.join(tmpdir, 'a')
    second = os.path.join(tmpdir, 'd')
    third = os.path.join(tmpdir, 'g')
    tree = FSTree.at_path(first, {first, second, third})
    assert tree == FSTree({
        'b': FSTree({
            'c': FSTree({
                'e': FSTree({
                    'f': FSTree({
                        'h': FSTree({
                            'i': None,
                        }),
                    }),
                }),
            }),
        }),
    })


def test_triple_linked_invalids(triple_linked):
    """
    Test linking across three trees, where 0-2 of of them are not valid roots.
    """
    _, tmpdir = triple_linked
    first = os.path.join(tmpdir, 'a')
    second = os.path.join(tmpdir, 'd')
    third = os.path.join(tmpdir, 'g')
    for nope in (
        set(),
        {first},
        {second},
        {third},
        {first, second},
        {first, third},
        {second, third},
    ):
        tree = FSTree.at_path(first, valid_roots=nope)
        assert tree == FSTree({})


def test_foobar(with_suffixes):
    _, tmpdir = with_suffixes
    tree = FSTree.at_path(tmpdir, {tmpdir})
    assert tree == FSTree({
        'foo': FSTree({
            'bar.md': None,
            'moo': FSTree({
                'BAR.MD': None,
                'thing': None,
                'zoo': FSTree({
                    'BAR.md': None,
                    'BAR.RST': None,
                }),
            }),
        }),
        'fred': FSTree({
            'blah.txt': None,
            'klang.rst': None,
            'wuub': None,
        }),
    })
