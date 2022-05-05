from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="JIG",
    settings_files=["settings.yaml", ".secrets.yaml"],
    environments=True,
    env_switcher="JIG_ENV",
    default_env="dev",
    merge_enabled=True,
    validators=[
        Validator("app.test_firmware_path", "app.stage", must_exist=True),
        Validator(
            "device.minter_id",
            "device.thing_type_name",
            "device.thing_type_id",
            "device.hw_revision",
            "device.assembly_id",
            "device.assembly_version",
            "device.manufacturer_name",
            "device.manufacturer_id",
            must_exist=True,
        ),
        Validator("api.region", "api.host", must_exist=True),
        Validator("lora.join_eui", must_exist=True),
        # should not be present outside of development as it will be generated uniquely for each device
        Validator("lora.app_key", must_exist=None),
    ],
)
