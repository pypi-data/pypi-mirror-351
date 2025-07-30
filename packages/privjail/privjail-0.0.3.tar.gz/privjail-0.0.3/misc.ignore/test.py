from typing import get_origin, get_args, Union, Any

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

    # 左も右も Union の場合：左の要素全部が右のいずれかに含まれるか
    if origin1 is Union and origin2 is Union:
        return all(any(is_subtype(t1, t2) for t2 in args2) for t1 in args1)

    # 右側だけ Union の場合：左がその中のどれかに含まれれば OK
    if origin2 is Union:
        return any(is_subtype(type1, t2) for t2 in args2)

    # 左側だけ Union の場合：左の全要素が右に合うか
    if origin1 is Union:
        return all(is_subtype(t1, type2) for t1 in args1)

    # ジェネリック型（List, Dict, Tuple など）
    if origin1 == origin2:
        if len(args1) != len(args2):
            return False
        return all(is_subtype(a1, a2) for a1, a2 in zip(args1, args2))

    raise Exception

from typing import List, Tuple, Dict, Union, Any

assert is_subtype(int, Union[int, str, float])       # ✅ True
assert is_subtype(str, Union[int, str, float])       # ✅ True
assert not is_subtype(List[int], List[str])          # ✅ True → 型パラメータが違う
assert is_subtype(List[int], List[Any])              # ✅ True
assert not is_subtype(List[Any], List[int])          # ✅ False
assert is_subtype(Dict[str, int], Dict[str, Any])    # ✅ True
assert not is_subtype(Dict[str, Any], Dict[str, int])# ✅ False
assert is_subtype(Union[int, str], Union[int, str, float])  # ✅ True
assert not is_subtype(Union[int, str, float], Union[int, str])  # ✅ False
assert is_subtype(Tuple[int, str], Tuple[Any, Any]) # ✅ True
assert not is_subtype(Tuple[int, str], Tuple[int, int]) # ✅ False

assert is_subtype(Union[int, int], int)       # ✅ True
assert not is_subtype(Union[float, int], int)       # ✅ True
