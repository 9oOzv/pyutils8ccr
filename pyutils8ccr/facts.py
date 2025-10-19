from pathlib import Path


def xdg_config_home() -> Path:
    from pathlib import Path
    import os
    return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
