config = __spec__.loader.config
if "unit_test" not in config.invocation_params.args[0] and "unit_test" not in config.invocation_dir.dirname:
    pytest_plugins = [
        "common.hooks"
    ]
