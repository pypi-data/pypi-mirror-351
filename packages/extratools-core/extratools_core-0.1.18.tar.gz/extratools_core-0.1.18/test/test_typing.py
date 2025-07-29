from pathlib import Path, PurePath

from extratools_core.typing import PathLike, PurePathLike


def test_PurePathLike() -> None:  # noqa: N802
    class Test:
        ...
    assert not isinstance(Test(), PurePathLike)

    assert isinstance(PurePath(), PurePathLike)
    assert isinstance(Path(), PurePathLike)


def test_PathLike() -> None:  # noqa: N802
    class Test:
        ...
    assert not isinstance(Test(), PathLike)

    assert not isinstance(PurePath(), PathLike)
    assert isinstance(Path(), PathLike)
