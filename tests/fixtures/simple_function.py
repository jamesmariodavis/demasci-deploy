from typing import (
    Dict,
    Union,
)


def some_f(
    x: int,
    y: str,
    use_cache_a_lache: bool,  # pylint: disable=unused-argument
    z: int = 4,
) -> Dict[int, Union[int, str]]:
    return {x: y, z: z}
