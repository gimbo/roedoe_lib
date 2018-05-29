"""
Tests of FSTree.dict(), FSTree.undict(), FSTree.to_json(),
and FSTree.from_json() - basically testing that they produce fixpoints.
"""


from roedoe_lib import FSTree


def test_empty():
    """Test empty tree."""
    dict_undict_loops({
        'contents': {},
    })


def test_empty_with_metadata():
    """Test empty tree with metadata."""
    dict_undict_loops({
        'contents': {},
        'metadata': 'Fake metadata',
    })


def test_simple():
    """Test a simple tree."""
    dict_undict_loops({
        'contents': {
            'a': None,
            'b': None,
            'c': None,
        },
    })


def test_simple_nested():
    """Test a simple tree with a bit of nesting."""
    dict_undict_loops({
        'contents': {
            'a': {
                'contents': {
                    'aa': None,
                },
                'metadata': 'a meta',
            },
            'b': {
                'contents': {},
            },
            'c': None,
        },
        'metadata': 'meta',
    })


def test_basic(basic):
    """Test basic tree with not much drama."""
    spec, _ = basic
    dict_for_tree = spec_to_tree_for_dict(spec)
    dict_undict_loops(dict_for_tree)


def test_mutual_empty(mutual_empty):
    """Test two mutually recursive linked trees with no files."""
    spec, _ = mutual_empty
    dict_for_tree = spec_to_tree_for_dict(spec)
    dict_undict_loops(dict_for_tree)


def test_mutual_one_file(mutual_one_file):
    """Test two mutually recursive linked trees with one file."""
    spec, _ = mutual_one_file
    dict_for_tree = spec_to_tree_for_dict(spec)
    dict_undict_loops(dict_for_tree)


def test_triple_linked(triple_linked):
    """Test link across three trees."""
    spec, _ = triple_linked
    dict_for_tree = spec_to_tree_for_dict(spec)
    dict_undict_loops(dict_for_tree)


def test_with_suffixes(with_suffixes):
    """Test a tree with filenames with suffixes."""
    spec, _ = with_suffixes
    dict_for_tree = spec_to_tree_for_dict(spec)
    dict_undict_loops(dict_for_tree)


def dict_undict_loops(dict_for_tree):
    """
    Given a dict suitable for FSTree.undict(), put it through a couple of
    cycles.
    """
    # First check undict/dict loop
    tree = FSTree.undict(dict_for_tree)
    dict_from_tree = tree.dict
    assert dict_from_tree == dict_for_tree
    # Then check dict/undict loop
    fixpoint = FSTree.undict(dict_from_tree)
    assert fixpoint == tree
    # Then check to_json/from_json loop
    json_from_tree = tree.to_json()
    tree_from_json = FSTree.from_json(json_from_tree)
    assert tree_from_json == tree
    # Finally check from_json/to_json loop
    json_fixpoint = tree_from_json.to_json()
    assert json_fixpoint == json_from_tree


def spec_to_tree_for_dict(tree_for_dict):

    """
    Given a spec from a test fixture, turn it into a dict suitable for
    dict_undict_loops().
    """

    def process_value(v):
        if isinstance(v, dict):
            return recursive_wibwab(v)
        elif v is None:
            return v
        else:
            # If it's a link or whatever, just return the string representation.
            return str(v)

    def recursive_wibwab(tree):
        contents = {
            k: process_value(v)
            for k, v in tree.items()
        }
        return {
            'contents': contents,
            'metadata': 'fake metadata for test',
        }

    return recursive_wibwab(tree_for_dict)
