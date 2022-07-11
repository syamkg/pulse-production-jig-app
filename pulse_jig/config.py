from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="JIG",
    settings_files=["settings.yaml", ".secrets.yaml"],
    validators=[
        Validator("app.test_firmware_path", must_exist=True),
        Validator(
            "device.minter_id",
            "device.thing_type_name",
            "device.thing_type_id",
            "device.hw_revision",
            "device.assembly_id",
            "device.assembly_version",
            "device.manufacturer_name",
            "device.manufacturer_id",
            "device.iecex_cert",
            must_exist=True,
        ),
        Validator("api.region", "api.host", "api.stage", must_exist=True),
        Validator("lora.join_eui", must_exist=True),
        # app_key should not be present outside of development as it will be generated uniquely for each device
        Validator("lora.app_key", must_exist=None),
        Validator("VERSION", must_exist=True),
    ],
)
