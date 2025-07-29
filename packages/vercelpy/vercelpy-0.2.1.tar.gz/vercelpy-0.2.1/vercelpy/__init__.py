"""
vercelpy is a Python Wrapper around the Vercel Storage APIs. 

vercelpy.blob_store is a wrapper around the Vercel Blob API.
>>> from vercelpy import blob_store
>>> blob_store.upload_file("test.txt", "test")

vercelpy.edge_config is a wrapper around the Vercel Edge Config API.
>>> from vercelpy import edge_config
>>> edge_config.get("test")



Source & Documentation: https://github.com/SuryaSekhar14/vercelpy
"""

from . import blob_store
from . import edge_config

__author__ = 'Surya Sekhar Datta <hello@surya.dev>'
__version__ = '0.2.0'
__package__ = 'vercelpy'