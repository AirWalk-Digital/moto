from __future__ import unicode_literals
from .responses import InspectorResponse

url_bases = ["https?://inspector.(.+).amazonaws.com"]

url_paths = {"{0}/$": InspectorResponse.dispatch}