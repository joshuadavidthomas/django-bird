from __future__ import annotations

from django_bird import hookimpl
from django_bird.apps import DjangoBirdAppConfig
from django_bird.plugins import pm


class TestAppReadyHooks:
    def test_pre_ready_and_ready_hooks(self):
        called = []

        class LifecyclePlugin:
            @hookimpl
            def pre_ready(self):
                return lambda: called.append("pre_ready")

            @hookimpl
            def ready(self):
                return lambda: called.append("ready")

        pm.register(LifecyclePlugin(), name="LifecyclePlugin")

        try:
            app = DjangoBirdAppConfig("django_bird", __import__("django_bird"))
            app.ready()

            assert "pre_ready" in called
            assert "ready" in called
        finally:
            pm.unregister(name="LifecyclePlugin")
