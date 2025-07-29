import json
import toml
import os

def load_config(path):
    if not os.path.exists(path):
        print(f"❌ Error: Config file '{path}' not found.")
        exit(1)

    _, ext = os.path.splitext(path)
    if ext == ".json":
        with open(path, "r") as f:
            return json.load(f)
    elif ext == ".toml":
        with open(path, "r") as f:
            return toml.load(f)
    elif ext == ".py":
        config = {}
        exec(open(path).read(), config)
        return config
    else:
        print(f"❌ Error: Unsupported config file format '{ext}'. Use JSON, TOML, or Python files.")
        exit(1)
