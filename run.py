# Native imports
import multiprocessing

# 3rd party imports
from gunicorn.app.base import BaseApplication

# Project imports
from app import create_app
from app.config import settings, Env


def number_of_workers():
    """
    Calculate number of workers based on CPU count.
    """
    if settings.workers:
        return settings.workers
    else:
        return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(BaseApplication):
    def __init__(self, application, opts=None):
        self.options = opts or {}
        self.application = application
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


app = create_app()

if __name__ == "__main__":
    if settings.app_env == Env.Dev:
        app.run(host="0.0.0.0")
    else:
        options = {
            "bind": f"0.0.0.0:{str(settings.app_port)}",
            "workers": number_of_workers(),
        }
        StandaloneApplication(app, options).run()
