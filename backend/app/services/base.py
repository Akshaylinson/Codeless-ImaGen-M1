from __future__ import annotations

import logging
from contextlib import AbstractContextManager


logger = logging.getLogger(__name__)


class ModelService(AbstractContextManager):
    model_name: str = "generic"

    def __enter__(self):
        self.load_model()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.cleanup()
        self.unload_model()
        return False

    def load_model(self) -> None:
        logger.info("Model loaded: %s", self.model_name)

    def predict(self, *args, **kwargs):
        raise NotImplementedError

    def cleanup(self) -> None:
        logger.info("Cleanup complete: %s", self.model_name)

    def unload_model(self) -> None:
        logger.info("Model unloaded: %s", self.model_name)

