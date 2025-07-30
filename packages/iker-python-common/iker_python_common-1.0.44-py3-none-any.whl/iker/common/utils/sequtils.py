import functools
import itertools
from collections import deque
from collections.abc import Callable, Generator, Iterable, Iterator, Sequence, Sized
from typing import Generic, TypeVar

__all__ = [
    "head",
    "head_or_none",
    "last",
    "last_or_none",
    "tail",
    "tail_iter",
    "init",
    "init_iter",
    "some",
    "scan_left",
    "scan_right",
    "fold_left",
    "fold_right",
    "slide_left",
    "slide_right",
    "grouped",
    "deduped",
    "batch_yield",
    "chunk",
    "chunk_between",
    "chunk_with_key",
    "merge_chunks",
    "Seq",
    "seq",
]

T = TypeVar("T")
KT = TypeVar("KT")
VT = TypeVar("VT")
TT = TypeVar("TT")
Tco = TypeVar("Tco", covariant=True)


# See Haskell's list operations head, tail, init, and last
# which is also provided in Scala list operations

def head(ms: Sequence[T]) -> T:
    return ms[0]


def head_or_none(ms: Sequence[T]) -> T | None:
    if len(ms) > 0:
        return ms[0]
    return None


def last(ms: Sequence[T]) -> T:
    return ms[-1]


def last_or_none(ms: Sequence[T]) -> T | None:
    if len(ms) > 0:
        return ms[-1]
    return None


def tail(ms: Sequence[T]) -> Sequence[T]:
    return ms[1:]


def tail_iter(ms: Iterable[T]) -> Generator[T, None, None]:
    it = iter(ms)
    try:
        next(it)
        while True:
            yield next(it)
    except StopIteration:
        return


def init(ms: Sequence[T]) -> Sequence[T]:
    return ms[:-1]


def init_iter(ms: Iterable[T]) -> Generator[T, None, None]:
    it = iter(ms)
    try:
        prev = next(it)
    except StopIteration:
        return
    for this in it:
        yield prev
        prev = this


def some(x: T, test: Callable[[T], bool] = lambda x: x is not None) -> Generator[T, None, None]:
    if test(x):
        yield x


def scan_left(data: Sequence[T], zero: TT | None, func: Callable[[TT, T], TT]) -> Generator[TT, None, None]:
    accum = zero
    for elem in data:
        accum = func(accum, elem)
        yield accum


def scan_right(data: Sequence[T], zero: TT | None, func: Callable[[TT, T], TT]) -> Generator[TT, None, None]:
    accum = zero
    for elem in reversed(data):
        accum = func(accum, elem)
        yield accum


def fold_left(data: Sequence[T], zero: TT | None, func: Callable[[TT, T], TT]) -> TT | None:
    if len(data) == 0:
        return zero
    it = tail_iter(data) if zero is None else data
    accum = head(data) if zero is None else zero
    for elem in it:
        accum = func(accum, elem)
    return accum


def fold_right(data: Sequence[T], zero: TT | None, func: Callable[[TT, T], TT]) -> TT | None:
    if len(data) == 0:
        return zero
    it = tail_iter(reversed(data)) if zero is None else reversed(data)
    accum = last(data) if zero is None else zero
    for elem in it:
        accum = func(accum, elem)
    return accum


def slide_left(
    data: Sequence[T],
    window: int,
    func: Callable[[Iterable[T]], TT] = lambda x: x,
    *,
    allow_partial: tuple[bool, bool] = (False, False),
    padding: tuple[T, T] = (None, None),
) -> Generator[TT, None, None]:
    init_partial, tail_partial = allow_partial

    if window <= 0:
        return
    if not init_partial and not tail_partial and window > len(data):
        return

    init_padding, tail_padding = padding

    if init_partial and init_padding is not None:
        init_partial = False
        data = list(itertools.chain(itertools.repeat(init_padding, window - 1), data))
    if tail_partial and tail_padding is not None:
        tail_partial = False
        data = list(itertools.chain(data, itertools.repeat(tail_padding, window - 1)))

    if init_partial:
        yield from (func(data[:i]) for i in range(1, min(window, len(data))))

    if window > len(data):
        if init_partial:
            yield func(data)
        if init_partial and tail_partial:
            yield from (func(data) for _ in range(window - len(data) - 1))
        if tail_partial:
            yield func(data)
    else:
        it = iter(data)
        d = deque(itertools.islice(it, window), maxlen=window)
        yield func(d)
        for x in it:
            d.append(x)
            yield func(d)

    if tail_partial:
        yield from (func(data[-i:]) for i in reversed(range(1, min(window, len(data)))))


def slide_right(
    data: Sequence[T],
    window: int,
    func: Callable[[Iterable[T]], TT] = lambda x: x,
    *,
    allow_partial: tuple[bool, bool] = (False, False),
    padding: tuple[T, T] = (None, None),
) -> Generator[TT, None, None]:
    init_partial, tail_partial = allow_partial

    if window <= 0:
        return
    if not init_partial and not tail_partial and window > len(data):
        return

    init_padding, tail_padding = padding

    if init_partial and init_padding is not None:
        init_partial = False
        data = list(itertools.chain(itertools.repeat(init_padding, window - 1), data))
    if tail_partial and tail_padding is not None:
        tail_partial = False
        data = list(itertools.chain(data, itertools.repeat(tail_padding, window - 1)))

    if tail_partial:
        yield from (func(data[-i:]) for i in range(1, min(window, len(data))))

    if window > len(data):
        if tail_partial:
            yield func(data)
        if init_partial and tail_partial:
            yield from (func(data) for _ in range(window - len(data) - 1))
        if init_partial:
            yield func(data)
    else:
        it = reversed(data)
        d = deque(itertools.islice(it, window), maxlen=window)
        yield func(reversed(d))
        for x in it:
            d.append(x)
            yield func(reversed(d))

    if init_partial:
        yield from (func(data[:i]) for i in reversed(range(1, min(window, len(data)))))


def grouped(
    ms: Sequence[T],
    key_func: Callable[[T], KT],
    keys_ordered: bool = False,
    values_only: bool = False,
) -> list[tuple[KT, list[T]]] | list[list[T]]:
    """
    Groups the given list of elements according to key generator function

    :param ms: list of elements
    :param key_func: key generator function
    :param keys_ordered: True if the return elements are sorted according to the keys
    :param values_only: True if only return elements groups without corresponding keys
    :return: grouped elements, with corresponding keys if `values_only` is set to False
    """
    if ms is None or len(ms) == 0:
        return []
    grouped_ms: dict[KT, list[T]] = {}
    for m in ms:
        k = key_func(m)
        grouped_ms.setdefault(k, []).append(m)
    groups = sorted(grouped_ms.items()) if keys_ordered else grouped_ms.items()
    return [d for _, d in groups] if values_only else [(k, d) for k, d in groups]


def deduped(ms: Sequence[T], comp_func: Callable[[T, T], bool]) -> list[T]:
    """
    Dedupes the given list of elements

    :param ms: list of elements
    :param comp_func: comparator generator function
    :return: deduped elements
    """
    if ms is None or len(ms) == 0:
        return []
    deduped_ms: list[T] = [head(ms)]
    for m in tail_iter(ms):
        if not comp_func(last(deduped_ms), m):
            deduped_ms.append(m)
    return deduped_ms


def batch_yield(ms: Iterable[T], batch_size: int) -> Generator[list[T], None, None]:
    """
    Splits the given input sequence into batches according to the specific batch size

    :param ms: sequence of elements
    :param batch_size: batch size
    :return: batches of sequences
    """
    if batch_size < 1:
        raise ValueError("illegal batch size")
    batch: list[T] = []
    for m in ms:
        batch.append(m)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if len(batch) > 0:
        yield batch


def chunk(ms: Sequence[T], chunk_func: Callable[[Sequence[T], T], bool], exclusive_end: bool = False) -> list[list[T]]:
    """
    Chops the list of elements into chunks

    :param ms: list of elements
    :param chunk_func: chunk generator function with compares the current chunk and the next element from the list
    :param exclusive_end: set to true to make each chunk (except the last one) carrying the first element of
    the next chunk as an exclusive end
    :return: list of element chunks
    """
    if ms is None or len(ms) == 0:
        return []
    chunks: list[list[T]] = [[head(ms)]]
    for m in tail_iter(ms):
        if chunk_func(last(chunks), m):
            if exclusive_end:
                last(chunks).append(m)
            chunks.append([m])
        else:
            last(chunks).append(m)
    return chunks


def chunk_between(ms: Sequence[T], chunk_func: Callable[[T, T], bool], exclusive_end: bool = False) -> list[list[T]]:
    return chunk(ms, lambda x, y: chunk_func(last(x), y), exclusive_end)


def chunk_with_key(ms: Sequence[T], key_func: Callable[[T], KT], exclusive_end: bool = False) -> list[list[T]]:
    return chunk_between(ms, lambda x, y: key_func(x) != key_func(y), exclusive_end)


def merge_chunks(
    chunks: Sequence[Sequence[T]],
    merge_func: Callable[[Sequence[T], Sequence[T]], bool],
    drop_exclusive_end: bool = False,
) -> list[list[T]]:
    """
    Merges chunks according to the given merging criteria

    :param chunks: chunks to be merged into larger ones
    :param merge_func: merged chunk generator function
    :param drop_exclusive_end: set to true if each of the given chunk (except the last one) as an exclusive end element,
    and these exclusive end elements will be dropped while merging their chunks to the corresponding next chunks
    :return: merged chunks
    """
    if chunks is None or len(chunks) == 0:
        return []

    merged_chunks: list[list[T]] = []

    def stateful_reducer(a: Sequence[T], b: Sequence[T]) -> Sequence[T]:
        if merge_func(a, b):
            if drop_exclusive_end:
                return list(itertools.chain(init_iter(a), b))
            return list(itertools.chain(a, b))
        else:
            merged_chunks.append(list(a))
            return b

    last_chunk = functools.reduce(stateful_reducer, chunks)
    merged_chunks.append(list(last_chunk))
    return merged_chunks


SeqT = TypeVar("SeqT", bound="Seq")


class Seq(Generic[Tco], Sequence[Tco], Sized):
    def __init__(self, data: Iterable[Tco] | SeqT):
        if isinstance(data, Seq):
            self.data = data.data
        elif isinstance(data, Iterable):
            self.data = list(data)
        else:
            raise ValueError("unsupported data type")

    @property
    def size(self) -> int:
        return len(self.data)

    @property
    def empty(self) -> bool:
        return self.size == 0

    def __add__(self: SeqT, other: SeqT) -> SeqT:
        return self.concat(other)

    def __getitem__(self: SeqT, item: int | slice) -> SeqT:
        if isinstance(item, slice):
            return type(self)(self.data[item])
        elif isinstance(item, int):
            return type(self)(some(self.data[item]))
        raise ValueError("unsupported index type")

    def __len__(self) -> int:
        return len(self.data)

    def __contains__(self, item) -> bool:
        return item in self.data

    def __iter__(self) -> Iterator[Tco]:
        return iter(self.data)

    def __reversed__(self) -> Iterator[Tco]:
        return reversed(self.data)

    def count(self, elem: Tco):
        return self.count_if(lambda x: x == elem)

    def count_if(self, func: Callable[[Tco], bool]):
        return sum(1 for item in self.data if func(item))

    def concat(self: SeqT, other: SeqT) -> SeqT:
        return type(self)(itertools.chain(self.data, other.data))

    def take_left(self: SeqT, n: int) -> SeqT:
        if n <= 0:
            return type(self)([])
        return self[:n]

    def take_right(self: SeqT, n: int) -> SeqT:
        if n <= 0:
            return type(self)([])
        return self[-n:]

    take = take_left

    def reverse(self: SeqT) -> SeqT:
        return type(self)(reversed(self.data))

    def distinct(self: SeqT) -> SeqT:
        return type(self)(sorted(set(self.data)))

    def scan_left(self, zero: TT | None, func: Callable[[TT, Tco], TT]) -> "Seq[TT]":
        return Seq(scan_left(self.data, zero, func))

    def scan_right(self, zero: TT | None, func: Callable[[TT, Tco], TT]) -> "Seq[TT]":
        return Seq(scan_right(self.data, zero, func))

    scan = scan_left

    def map(self, func: Callable[[Tco], TT]) -> "Seq[TT]":
        return self.scan(None, lambda x, y: func(y))

    def fold_left(self, zero: TT | None, func: Callable[[TT, Tco], TT]) -> "Seq[TT]":
        return Seq(some(fold_left(self.data, zero, func)))

    def fold_right(self, zero: TT | None, func: Callable[[TT, Tco], TT]) -> "Seq[TT]":
        return Seq(some(fold_right(self.data, zero, func)))

    fold = fold_left

    def slide_left(
        self,
        window: int,
        func: Callable[[Iterable[Tco]], TT] = lambda x: x,
        *,
        allow_partial: tuple[bool, bool] = (False, False),
        padding: tuple[Tco, Tco] = (None, None),
    ) -> "Seq[TT]":
        return Seq(slide_left(self.data, window, func, allow_partial=allow_partial, padding=padding))

    def slide_right(
        self,
        window: int,
        func: Callable[[Iterable[Tco]], TT] = lambda x: x,
        *,
        allow_partial: tuple[bool, bool] = (False, False),
        padding: tuple[Tco, Tco] = (None, None),
    ) -> "Seq[TT]":
        return Seq(slide_right(self.data, window, func, allow_partial=allow_partial, padding=padding))

    slide = slide_left

    def reduce(self: SeqT, func: Callable[[Tco, Tco], Tco]) -> SeqT:
        return type(self)(self.fold(None, lambda x, y: func(x, y)))

    def max(self: SeqT, func: Callable[[Tco, Tco], bool] = None) -> SeqT:
        func = func or (lambda x, y: x > y)
        return self.reduce(lambda x, y: x if func(x, y) else y)

    def min(self: SeqT, func: Callable[[Tco, Tco], bool] = None) -> SeqT:
        func = func or (lambda x, y: x < y)
        return self.reduce(lambda x, y: x if func(x, y) else y)

    def group(self, func: Callable[[Tco], KT]) -> "Seq[tuple[KT, list[Tco]]]":
        return Seq(grouped(self.data, key_func=func, keys_ordered=True))

    def keys(self):
        return Seq(key for key, _ in self.data)

    def values(self):
        return Seq(value for _, value in self.data)

    def swap(self):
        return Seq((value, key) for key, value in self.data)

    def map_keys(self, func: Callable[[Tco], TT]):
        return Seq((func(key), value) for key, value in self.data)

    def map_values(self, func: Callable[[Tco], TT]):
        return Seq((key, func(value)) for key, value in self.data)

    def flat_map(self, func: Callable[[Tco], Iterable[TT]]) -> "Seq[TT]":
        data = []
        for d in self.data:
            data.extend(func(d))
        return Seq(data)

    def flatten(self):
        return self.flat_map(lambda x: list(x))

    def group_map(self, group_func: Callable[[Tco], KT], map_func: Callable[[Tco], TT]) -> "Seq[tuple[KT, list[TT]]]":
        return self.group(group_func).map_values(lambda x: list(map(map_func, x)))

    def filter(self: SeqT, func: Callable[[Tco], bool]) -> SeqT:
        return type(self)(filter(func, self.data))

    def filter_not(self: SeqT, func: Callable[[Tco], bool]) -> SeqT:
        return self.filter(lambda x: not func(x))

    def sort(self: SeqT, func: Callable[[Tco], KT]) -> SeqT:
        return type(self)(sorted(self.data, key=func))

    def head(self: SeqT) -> SeqT:
        return type(self)(some(head_or_none(self.data)))

    def last(self: SeqT) -> SeqT:
        return type(self)(some(last_or_none(self.data)))

    def init(self: SeqT) -> SeqT:
        return type(self)(init_iter(self.data))

    def tail(self: SeqT) -> SeqT:
        return type(self)(tail_iter(self.data))

    def foreach(self: SeqT, func: Callable[[Tco], None]) -> SeqT:
        for elem in self.data:
            func(elem)
        return self

    def exists(self, func: Callable[[Tco], bool]) -> "Seq[bool]":
        return Seq(some(any(map(func, self.data))))

    def forall(self, func: Callable[[Tco], bool]) -> "Seq[bool]":
        return Seq(some(all(map(func, self.data))))

    def union(self: SeqT, other: SeqT) -> SeqT:
        return type(self)(sorted(set(self.data).union(set(other.data))))

    def intersect(self: SeqT, other: SeqT) -> SeqT:
        return type(self)(sorted(set(self.data).intersection(set(other.data))))

    def zip(self, other: "Seq[TT]") -> "Seq[tuple[Tco, TT]]":
        return Seq(zip(self.data, other.data))

    def zip_fill(self, other: "Seq[TT]", fill: Tco | TT | None = None) -> "Seq[tuple[Tco, TT]]":
        return Seq(itertools.zip_longest(self.data, other.data, fillvalue=fill))


seq = Seq
