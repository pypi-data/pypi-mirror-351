# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    test_option.py                                     :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: dfine <coding@dfine.tech>                  +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/05/25 08:06:48 by dfine             #+#    #+#              #
#    Updated: 2025/05/27 22:19:09 by dfine            ###   ########.fr        #
#                                                                              #
# **************************************************************************** #


from typeric.option import NONE, NoneTypeError, Some, optiony, optiony_async
import pytest


def plus_one(x: int) -> int:
    return x + 1


def times_two(x: int) -> Some[int]:
    return Some(x * 2)


def test_some_basic():
    s = Some(42)
    assert s.is_some() is True
    assert s.is_none() is False
    assert s.unwrap() == 42
    assert s.unwrap_or(0) == 42
    assert s.map(plus_one) == Some(43)
    assert s.and_then(times_two) == Some(84)
    print("test_some_basic passed")


def test_none_basic():
    n = NONE
    assert n.is_some() is False
    assert n.is_none() is True
    try:
        n.unwrap()
        assert False, "unwrap on None should raise"
    except NoneTypeError as e:
        print(e)
    assert n.unwrap_or(100) == 100
    assert n.map(plus_one) is NONE
    assert n.and_then(times_two) is NONE
    print("test_none_basic passed")


def test_equality():
    assert Some(10) == Some(10)
    assert Some(10) != Some(11)
    assert NONE == NONE
    assert Some(10) != NONE
    print("test_equality passed")


@optiony
def might_return_none(x: int) -> str | None:
    return "ok" if x > 0 else None


def test_optiony_explicit_none():
    assert might_return_none(1) == Some("ok")
    assert might_return_none(0) is NONE


@optiony_async
async def async_maybe(x: int) -> str | None:
    return "yes" if x > 0 else None


@pytest.mark.asyncio
async def test_async_optiony_explicit_none():
    assert await async_maybe(1) == Some("yes")
    assert await async_maybe(0) is NONE


if __name__ == "__main__":
    test_some_basic()
    test_none_basic()
    test_equality()
