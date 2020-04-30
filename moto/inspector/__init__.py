from __future__ import unicode_literals
from .models import inspector_backends
from ..core.models import base_decorator, deprecated_base_decorator

inspector_backend = inspector_backends["us-east-1"]
mock_inspector = base_decorator(inspector_backends)
mock_inspector_deprecated = deprecated_base_decorator(inspector_backends)