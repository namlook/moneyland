from .settings import *

DEBUG = False

ALLOWED_HOSTS = ["*"]
STATIC_ROOT = "/home/moneyland/moneyland/public"
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

PIPELINE['CSS_COMPRESSOR'] = 'pipeline.compressors.NoopCompressor'
PIPELINE['JS_COMPRESSOR'] = 'pipeline.compressors.NoopCompressor'
