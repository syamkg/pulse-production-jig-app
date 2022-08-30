# Quick Reference Guide

### How to run the jig app (config environment) and update software & firmware of a jig?

1. Set the required environment variables & setting in `vars/environment_vars.yml`
2. Auth to `wpl-wrk-ias-prd`
3. Run `../scripts/download_firmware.sh`
4. Auth to `wpl-wrk-iasdevice-prd`
5. Run `update_jig.yml` playbook with AWS Account ID as extra vars if required (`-e "aws_account_id=xxxxxxx"`)

> Note: update_jig.yml will not overwrite the following environment config files
> 1. app.env
> 2. settings.local.yaml
> 3. settings.yaml
