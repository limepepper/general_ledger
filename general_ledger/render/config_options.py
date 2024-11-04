import yaml


class RenderOptions:
    def __init__(self, config=None, **overrides):
        self.config = config or {}
        self.overrides = overrides

    def get(self, key, default=None):
        # Check for runtime overrides first
        if key in self.overrides:
            return self.overrides[key]
        # Fall back to configuration file values
        return self.config.get(key, default)


class RendererConfig:
    def __init__(self, config_file="general_ledger/config.yml"):
        with open(config_file, "r") as file:
            self.config = yaml.safe_load(file)

    def get(self, renderer, key, default=None):
        return self.config.get("renderer", {}).get(renderer, {}).get(key, default)
