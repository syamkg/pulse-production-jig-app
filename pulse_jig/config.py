from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="JIG",
    settings_files=["settings.yaml", ".secrets.yaml"],
    validators=[
        Validator("app.target", must_exist=True, is_in=["pulse-r1b", "ta3k", "fake"]),
        Validator(
            "app.debug", "app.test_firmware_path", "app.skip_firmware_load", "app.hwspec_repair_mode", must_exist=True
        ),
        Validator("app.prod_firmware_path", must_exist=True, when=Validator("app.target", eq="pulse-r1b")),
        Validator(
            "app.hwspec_repair_mode",
            eq=False,
            when=Validator("app.target", eq="pulse-r1b") & Validator("mode_vars.pulse_test_phase", eq=2),
        ),
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
        Validator("mode_vars", must_exist=True),
        Validator("mode_vars.cable_length", must_exist=True, when=Validator("app.target", eq="ta3k")),
        Validator("api.region", "api.host", "api.stage", must_exist=True),
        Validator("lora.test.join_eui", "lora.test.app_key", "lora.config.join_eui", must_exist=True),
        Validator("network.ping_interval", must_exist=True),
        Validator("VERSION", must_exist=True),
    ],
)
