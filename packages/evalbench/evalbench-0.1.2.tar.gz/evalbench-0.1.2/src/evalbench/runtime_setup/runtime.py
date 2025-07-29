_active_config = None

# to maintain global/shared context
def set_config(cfg):
    global _active_config
    cfg.validate()
    _active_config = cfg

# to retrieve the global context
def get_config():
    if _active_config is None:
        raise RuntimeError("Configurations have not been initialized. Call `set_config(...)` first.")
    return _active_config