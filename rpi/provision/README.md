# Ansible guide

Trying to give an in-depth guide to how the Ansible has set up & the order of execution AKA The Ansible Anatomy.

## Playbooks & Roles

we have 5 different playbooks executing various roles in different stages. 

In the order they should be executed & their roles, 
1. initialise
   1. basic-config
   2. change-passwords
   3. localisation
   4. set-hostname
   5. install-docker
2. initialise_dev (for `dev` only)
   1. add-ssh-key
   2. enable-wifi
3. ssm_agent
   1. ssm
   2. aws-credentials
4. initialise_prod (for `prod` only)
   1. disable-wifi
   2. remove-ssh-key
   3. disable-password-auth
   5. env-config
   6. app-launch
   4. update-firmware
5. maintenance 
   1. upgrade
   2. basic-config
   3. aws-credentials
   4. env-config
   5. app-launch
   6. update-firmware

### Ansible variables 

In general, you don't have to change the `default` variables for any role. Not changing any of the `deafult` variables
will help us to maintain the consistency between jigs.

You'll be prompt to enter instance specific values for each playbook if required. 

`initialise_prod` & `maintenance` will source an additional variable file `vars/environment_vars`. This will override 
the `default` values for, `env-config`, `app-launch` & `update-firmware`. Feel free to update these values as required.
