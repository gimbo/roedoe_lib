import functools
import json
import os

from pathspec import PathSpec


class FSTree:

    """A filesystem tree, with the potential for metadata at each level.

    This is essentially a nested dictionary representing the filesystem tree's
    contents.  At each level of the dictionary, keys which map to None are
    filenames, and keys which map to FSTree objects are directory names.  At
    each level there can be a piece of metadata also.

    """

    def __init__(self, contents, metadata=None):
        self.contents = contents
        self.metadata = metadata

    def __bool__(self):
        return bool(self.contents)

    def __repr__(self):
        return repr(self.contents)

    def __eq__(self, other):
        return all((
            self.contents == other.contents,
            self.metadata == other.metadata,
        ))

    def __getitem__(self, key):
        return self.contents[key]

    def __setitem__(self, key, value):
        self.contents[key] = value

    @property
    def dict(self):
        """Contents dictionary stripped of metadata."""
        result = {
            'contents': {
                k: v.dict if isinstance(v, FSTree) else v
                for k, v in self.contents.items()
            },
        }
        if self.metadata:
            result['metadata'] = self.metadata
        return result

    @classmethod
    def undict(cls, fstree_dict):
        """Dual of FSTree.dict()"""
        return FSTree(
            contents={
                k: cls.undict(v) if isinstance(v, dict) else v
                for k, v in fstree_dict['contents'].items()
            },
            metadata=fstree_dict.get('metadata'),
        )

    def to_json(self, *args, **kwargs):
        structure = {
            'type': 'FSTree',
            'version': '1.0.0',
            'fstree': self.dict
        }
        return json.dumps(structure, *args, **kwargs)

    @classmethod
    def from_json(cls, fstree_json, *args, **kwargs):
        structure = json.loads(fstree_json, *args, **kwargs)
        if structure.get('type') != 'FSTree':
            raise ValueError(structure)
        return cls.undict(structure['fstree'])

    @classmethod
    def at_path(cls, top, valid_roots, ignores=None):
        """Turn a directory tree on fisk into an FSTree object.

        :param top: Path to top of direcotry tree to walk.

        :param valid_roots: a set of paths; only links whose real paths are
        under the real paths of these roots will be kept in the returned
        dictionary.

        :param ignores: An optional pathspec.PathSpec specifying paths to ignore.

        :rvalue tree: An FSTree object.
        """

        get_real_path = get_path_resolver(valid_roots)

        def ignored(path):
            """Test if some path is to be ignored."""
            if not ignores:
                return False
            # Note special case logic here for checking vs top level of tree.
            rel_path = os.path.relpath(path, top) if path != top else top
            return ignores.match_file(rel_path)

        def recursive_wibwab(path):
            tree = cls({})
            full_path = os.path.join(top, path)
            contents = os.listdir(full_path)
            for item in sorted(contents):
                item_path = os.path.join(full_path, item)
                if ignored(item_path):
                    continue
                real_path = get_real_path(item_path)
                if not real_path:
                    # Disallowed destination; skip it
                    continue
                if real_path in seen:
                    continue
                seen.add(real_path)
                if os.path.isdir(item_path):
                    dir_tree = recursive_wibwab(item_path)
                    if dir_tree:
                        tree[item] = dir_tree
                elif os.path.isfile(item_path):
                    tree[item] = None
            return tree

        # First check that this whole directory is not supposed to be ignored
        # and that it's under one of the valid roots.
        if ignored(top) or not get_real_path(top):
            return cls({})

        seen = set()
        return recursive_wibwab('')

    def filter(self, filters):
        """
        Filter an FSTree object according to filename patterns.

        :param tree: an FSTree returned by FSTree.at_path()

        :param filters: a list of compiled regex objects, the filters to be
        applied.

        :return filtered: a copy of tree without: 1) files whose paths within
        the tree (relative to its root - these are not absolute/real paths)
        don't match any of the given filters, and 2) directories which are
        then empty.

        """

        if not filters:
            return self

        tree = self.dict

        def getitem_in_contents(container, key):
            return container['contents'][key]

        def recursive_filter_wibwab(path):
            if path:
                parts = path.split('/') if path else []
                subtree = functools.reduce(getitem_in_contents, parts, tree)
            else:
                subtree = tree
            filtered = {}
            contents = subtree['contents']
            metadata = subtree.get('metadata')
            for item, value in contents.items():
                item_path = os.path.join(path, item)
                if value is None:
                    if any((filter_.match(item_path) for filter_ in filters)):
                        filtered[item] = value
                elif isinstance(value, dict):
                    item_dict = recursive_filter_wibwab(item_path)
                    if item_dict['contents']:
                        filtered[item] = item_dict
            result = {
                'contents': filtered,
            }
            if metadata:
                result['metadata'] = metadata
            return result

        return FSTree.undict(recursive_filter_wibwab(''))


def get_path_resolver(roots):

    """
    Given some roots, return a function to compute the real path of some path,
    following links; if real path is not inside one of the roots, return None.
    """

    real_roots = [os.path.realpath(root) for root in roots]

    def get_real_path(path):
        """
        Compute real path of some path, following links; if real path is not
        inside one of real_roots, return None.
        """
        _real_path = os.path.realpath(path)
        if any((_real_path.startswith(root) for root in real_roots)):
            return _real_path

    return get_real_path


def ignore(*args):
    return PathSpec.from_lines('gitwildmatch', args)
