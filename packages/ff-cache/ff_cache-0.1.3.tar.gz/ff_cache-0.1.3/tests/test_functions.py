from datetime import datetime, timedelta
from time import sleep, time

import pytest
from ff_cache.context import ContextManager
from ff_cache.functions import ttl_from_result
from ff_cache.constant import DATETIME_FORMAT
from ff_cache.decorator import cache
from ff_cache.memory_cache import MemoryCache


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    ContextManager._instance = None
    ContextManager.init(cache=MemoryCache())
    yield
    ContextManager._instance = None

class DataObject:
    pass

def test_ttl_from_result():
    args = ['a', 'b']
    kwargs = {'c': 'c', 'd': 'd'}

    dict_ttl = {"ttl": 10}
    assert ttl_from_result(result=dict_ttl, *args, **kwargs) == dict_ttl["ttl"]

    dict_expires_in = {"expires_in": 20}
    assert ttl_from_result(result=dict_expires_in) == dict_expires_in["expires_in"]

    obj_ttl = DataObject()
    obj_ttl.ttl = 30
    assert ttl_from_result(result=obj_ttl) == obj_ttl.ttl

    obj_expires_in = DataObject()
    obj_expires_in.expires_in = 40
    assert ttl_from_result(result=obj_expires_in) == obj_expires_in.expires_in

    now = datetime.now()
    exipred_at = now + timedelta(seconds=10)
    dict_expired_at = {"expired_at": exipred_at}
    ttl = ttl_from_result(result=dict_expired_at)
    assert ttl <= 10 and ttl >= 9
    
    now = datetime.now()
    exipred_at = now + timedelta(seconds=10)
    dict_expired_at_str = {"expired_at": exipred_at.strftime(DATETIME_FORMAT)}
    ttl = ttl_from_result(result=dict_expired_at_str)
    assert ttl <= 10 and ttl >= 9

    now = datetime.now()
    exipred_at = now + timedelta(seconds=10)
    obj_expired_at = DataObject()
    obj_expired_at.expired_at = exipred_at
    ttl = ttl_from_result(result=obj_expired_at)
    assert ttl <= 10 and ttl >= 9

    now = datetime.now()
    exipred_at = now + timedelta(seconds=10)
    obj_expired_at_str = DataObject()
    obj_expired_at_str.expired_at = exipred_at.strftime(DATETIME_FORMAT)
    ttl = ttl_from_result(result=obj_expired_at_str)
    assert ttl <= 10 and ttl >= 9

    dict_invalidate_expired_at = {"expired_at": "test"}
    assert 0 == ttl_from_result(result=dict_invalidate_expired_at)
    
    invalidate_ttl_result = {}
    assert 0 == ttl_from_result(result=invalidate_ttl_result)

@cache(ttl=ttl_from_result)
def get_time():
    return {"message": f"{time()}", "ttl": 5}

def test_get_cache_ttl_from_result():
    _time = get_time()
    sleep(1)
    assert _time == get_time()

    sleep(5)
    assert _time != get_time()