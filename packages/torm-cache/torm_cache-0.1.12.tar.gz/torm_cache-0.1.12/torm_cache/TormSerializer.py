from functools import partial

import msgpack
import orjson
from requests_cache.serializers.pipeline import SerializerPipeline, Stage
from requests_cache.serializers.preconf import make_stage

_orjson_pre = make_stage('cattr.preconf.orjson')

def _serializer(data):
    return msgpack.packb(data)

def _deserialize(data):
    return msgpack.unpackb(data)

def torm_serializer():
    return SerializerPipeline(
        stages=[
            _orjson_pre,
            Stage(dumps=partial(orjson.dumps), loads=orjson.loads),
        ],
        name="torm_serializer",
        is_binary=False
    )
