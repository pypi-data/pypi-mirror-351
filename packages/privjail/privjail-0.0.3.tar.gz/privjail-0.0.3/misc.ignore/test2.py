from typing import get_origin, get_args, Union, Any, Sequence, Mapping
import collections.abc

def is_subtype(type1, type2) -> bool:
    if type2 is Any:
        return True
    if type1 is Any:
        return False

    origin1, args1 = get_origin(type1), get_args(type1)
    origin2, args2 = get_origin(type2), get_args(type2)

    # 単純型の場合
    if origin1 is None and origin2 is None:
        try:
            return issubclass(type1, type2)
        except TypeError:
            return type1 == type2

    # 両方 Union
    if origin1 is Union and origin2 is Union:
        return all(any(is_subtype(t1, t2) for t2 in args2) for t1 in args1)

    # 右側が Union
    if origin2 is Union:
        return any(is_subtype(type1, t2) for t2 in args2)

    # 左側が Union
    if origin1 is Union:
        return all(is_subtype(t1, type2) for t1 in args1)

    # 両方ジェネリック型
    if origin1 == origin2 and args1 and args2:
        if issubclass(origin1, collections.abc.Sequence):
            # Sequence は共変
            return all(is_subtype(a1, a2) for a1, a2 in zip(args1, args2))
        elif issubclass(origin1, collections.abc.Mapping):
            # Mapping: key は厳密一致、value は共変
            if len(args1) != 2 or len(args2) != 2:
                return False
            key1, val1 = args1
            key2, val2 = args2
            return is_subtype(key1, key2) and is_subtype(val1, val2)
        else:
            # デフォルトは厳密一致
            return all(is_subtype(a1, a2) and is_subtype(a2, a1) for a1, a2 in zip(args1, args2))

    # 外側型の比較
    if origin1 and origin2:
        try:
            if not issubclass(origin1, origin2):
                return False
        except TypeError:
            if origin1 != origin2:
                return False
        if args1 or args2:
            if len(args1) != len(args2):
                return False
            return all(is_subtype(a1, a2) for a1, a2 in zip(args1, args2))
        return True

    return False

from typing import List, Tuple, Dict, Union, Any

assert is_subtype(int, Union[int, str, float])       # ✅ True
assert is_subtype(str, Union[int, str, float])       # ✅ True
assert not is_subtype(List[int], List[str])          # ✅ True → 型パラメータが違う
assert is_subtype(List[int], List[Any])              # ✅ True
assert not is_subtype(List[Any], List[int])          # ✅ False
assert is_subtype(Mapping[str, int], Mapping[str, Any])    # ✅ True
assert not is_subtype(Dict[str, Any], Dict[str, int])# ✅ False
assert is_subtype(Union[int, str], Union[int, str, float])  # ✅ True
assert not is_subtype(Union[int, str, float], Union[int, str])  # ✅ False
assert is_subtype(Tuple[int, str], Tuple[Any, Any]) # ✅ True
assert not is_subtype(Tuple[int, str], Tuple[int, int]) # ✅ False

assert is_subtype(Union[int, int], int)       # ✅ True
assert not is_subtype(Union[float, int], int)       # ✅ True


from typing import List, Dict, Sequence, Mapping, Union

assert is_subtype(List[int], Sequence[int])       # ✅ True
assert not is_subtype(List[int], Sequence[str])   # ✅ False
assert is_subtype(Dict[str, int], Mapping[str, int])  # ✅ True
assert not is_subtype(Dict[str, int], Mapping[str, str])  # ✅ False
assert is_subtype(int, Union[int, str])           # ✅ True
assert is_subtype(Union[int, str], Union[int, str, float]) # ✅ True
assert not is_subtype(Union[int, str, float], Union[int, str]) # ✅ False

from typing import List, Dict, Sequence, Mapping, Any, Union

assert is_subtype(Dict[str, int], Dict[str, Any])    # ✅ True
assert not is_subtype(Dict[str, Any], Dict[str, int])# ✅ False

assert is_subtype(Sequence[int], Sequence[Any])      # ✅ True
assert not is_subtype(Sequence[Any], Sequence[int])  # ✅ False

assert is_subtype(List[int], Sequence[int])          # ✅ True
assert not is_subtype(List[int], Sequence[str])      # ✅ False

assert is_subtype(Union[int, str], Union[int, str, float])  # ✅ True
assert not is_subtype(Union[int, str, float], Union[int, str]) # ✅ False

