import pytest
from kevin_toolbox.patches.for_test import check_consistency
from kevin_toolbox.computer_science.algorithm.cache_manager.cache import Cache_Base
from kevin_toolbox.computer_science.algorithm.cache_manager.variable import CACHE_BUILDER_REGISTRY


def test_memo_cache():
    print("test Memo_Cache")

    cache = CACHE_BUILDER_REGISTRY.get(name=":in_memory:Memo")()  # type: Cache_Base

    # 读写
    cache.write(key="1", value=1)
    cache[2] = "2"
    check_consistency(cache["1"], 1)
    check_consistency(cache.read(2), "2")
    # 禁止重复写入
    with pytest.raises(KeyError):
        cache.write(key="1", value=2)
    # 禁止读取/删除不存在条目
    with pytest.raises(KeyError):
        cache.read(key=1)
    with pytest.raises(KeyError):
        cache.remove(key=1)

    # 容量判断
    check_consistency(len(cache), 2)

    # 删除与命中判断
    check_consistency(cache.has("1"), True)
    check_consistency(cache.has(2), True)
    cache.remove(2)
    check_consistency(cache.has(2), False)

    # 清空
    cache.clear()
    check_consistency(len(cache), 0)
