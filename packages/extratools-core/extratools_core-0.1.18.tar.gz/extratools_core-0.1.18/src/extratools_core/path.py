from collections.abc import Iterable
from datetime import UTC, datetime, timedelta

from .typing import PathLike


def clear_dir(curr_dir: PathLike) -> None:
    """
    Based on example in https://docs.python.org/3/library/pathlib.html#pathlib.Path.walk
    """

    if not curr_dir.is_dir():
        raise ValueError

    for parent, dirs, files in curr_dir.walk(top_down=False):
        for filename in files:
            (parent / filename).unlink()
        for dirname in dirs:
            (parent / dirname).rmdir()


def rm_with_empty_parents(
    curr: PathLike,
    *,
    stop: PathLike | None = None,
) -> None:
    curr.unlink()

    for parent in curr.parents:
        if parent == stop:
            return

        if parent.is_dir() and next(iter(parent.iterdir()), None) is None:
            parent.rmdir()


def cleanup_dir_by_ttl(
    curr_dir: PathLike,
    ttl: timedelta | datetime,
    *,
    include_empty_parents: bool = True,
    return_before_delete: bool = False,
) -> Iterable[tuple[PathLike, datetime]]:
    if not curr_dir.is_dir():
        raise ValueError

    now: datetime = datetime.now(UTC)

    for parent, _, files in curr_dir.walk(top_down=False):
        for filename in files:
            f: PathLike = (parent / filename)

            last_modified_time: datetime = datetime.fromtimestamp(f.stat().st_mtime, UTC)
            if isinstance(ttl, timedelta):
                ttl = now - ttl

            if last_modified_time < ttl:
                if return_before_delete:
                    yield (f, last_modified_time)

                if include_empty_parents:
                    rm_with_empty_parents(f, stop=curr_dir)
                else:
                    f.unlink()

                if not return_before_delete:
                    yield (f, last_modified_time)
