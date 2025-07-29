from random import random
from uuid import uuid4

from extratools_core.test import is_proper_mapping, is_proper_mutable_mapping


def test_is_proper_mapping() -> None:
    is_proper_mapping(dict, key_cls=str, value_cls=int)

    is_proper_mapping(
        lambda: {str(uuid4()): random()},
        key_cls=lambda: str(uuid4()),
        value_cls=random,
    )


def test_is_proper_mutable_mapping() -> None:
    is_proper_mutable_mapping(dict, key_cls=str, value_cls=int)

    is_proper_mutable_mapping(
        lambda: {str(uuid4()): random()},
        key_cls=lambda: str(uuid4()),
        value_cls=random,
    )
