import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from prime_utils import first_n_primes, is_prime


def test_is_prime_basic_cases() -> None:
    assert is_prime(2) is True
    assert is_prime(3) is True
    assert is_prime(4) is False
    assert is_prime(1) is False
    assert is_prime(0) is False
    assert is_prime(-7) is False


def test_first_n_primes_sequence() -> None:
    expected = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert first_n_primes(10) == expected


def test_first_n_primes_increasing_size() -> None:
    assert first_n_primes(1) == [2]
    assert first_n_primes(2) == [2, 3]
    assert first_n_primes(3) == [2, 3, 5]


