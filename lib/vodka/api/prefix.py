import os
from pathlib import Path
from ..util import createAPIResponse


class WinePrefix:
    def __init__(self, path):
        self.path = Path(path)

    def create(self):
        try:
            self.path.mkdir(parents=True, exist_ok=True)
            return createAPIResponse(200, {"path": str(self.path)})
        except Exception as e:
            return createAPIResponse(500, None, str(e))

    def delete(self):
        try:
            if self.path.exists():
                # todo: delete path
                os.system(f"echo todo: delete path {self.path}")
            return createAPIResponse(200)
        except Exception as e:
            return createAPIResponse(500, None, str(e))
