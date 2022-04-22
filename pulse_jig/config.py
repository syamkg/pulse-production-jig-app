from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="JIG",
    settings_files=["settings.yaml", ".secrets.yaml"],
    validator=[
        Validator("lora.join_eui", must_exist=True),
        # should not be present outside of development as it will be generated uniquely for each device
        Validator("lora.app_key", must_exist=None),
    ],
)
