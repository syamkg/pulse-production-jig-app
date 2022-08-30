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
5. update_jig
   1. env-config
   2. app-launch
   3. upgrade
   4. update-firmware
   5. docker-pull

### Ansible variables 

`update_jig` will source an additional variable file `vars/environment_vars`. 
Feel free to update these values as required.
