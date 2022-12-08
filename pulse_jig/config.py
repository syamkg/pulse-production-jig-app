from dynaconf import Dynaconf, Validator

from lib.target import Target

settings = Dynaconf(
    envvar_prefix="JIG",
    settings_files=["settings.yaml", ".secrets.yaml"],
    validators=[
        Validator("app.target", must_exist=True, is_in=list(Target)),
        Validator(
            "app.debug", "app.test_firmware_path", "app.skip_firmware_load", "app.hwspec_repair_mode", must_exist=True
        ),
        Validator("app.allow_target_change", default=False),
        Validator(
            "app.allow_target_change",
            ne=True,
            when=Validator("app.target", is_in=[Target.TA3K, Target.TA6K, Target.TA11K]),
        ),
        Validator(
            "app.prod_firmware_path",
            must_exist=True,
            when=Validator("app.target", is_in=[Target.PULSE_PHASE_1, Target.PULSE_PHASE_2, Target.PULSE_PHASE_3]),
        ),
        Validator(
            "app.hwspec_repair_mode",
            eq=False,
            when=Validator("app.target", is_in=[Target.PULSE_PHASE_2, Target.PULSE_PHASE_3]),
        ),
        Validator("app.test_port_min_threshold", default=0.4),
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
        Validator("mode_vars", must_exist=True),
        Validator("mode_vars.iecex_cert", must_exist=True, default="N/A"),
        Validator(
            "mode_vars.cable_length",
            must_exist=True,
            when=Validator("app.target", is_in=[Target.TA3K, Target.TA6K, Target.TA11K]),
        ),
        Validator("api.region", "api.host", "api.stage", must_exist=True),
        Validator("lora.test.join_eui", "lora.test.app_key", "lora.config.join_eui", must_exist=True),
        Validator("network.ping_interval", must_exist=True),
        Validator("VERSION", must_exist=True),
    ],
)
