from random import random
from uuid import uuid4

from extratools_core.test import is_proper_mapping, is_proper_mutable_mapping
from extratools_core.trie import TrieDict


def test_TrieDict() -> None:  # noqa: N802
    is_proper_mapping(TrieDict, key_cls=str, value_cls=int)

    is_proper_mapping(
        lambda: TrieDict({str(uuid4()): random()}),
        key_cls=lambda: str(uuid4()),
        value_cls=random,
    )

    is_proper_mutable_mapping(dict, key_cls=str, value_cls=int)

    is_proper_mutable_mapping(
        lambda: TrieDict({str(uuid4()): random()}),
        key_cls=lambda: str(uuid4()),
        value_cls=random,
    )
