# Raspberry Pi Provisioner

Here,  we'll discuss how to provision a new SD card to be used in a Jig plus some basic instructions to use Ansible 
for the first time.

## Creating Base Image

### STEP 1
Spin-up & SSH into the Vagrant box if you are not using Linux.
```shell
vagrant up && vagrant ssh
cd base_image
```

### STEP 2
Run the script with `sudo`.
```shell
sudo ./init-base.sh
```

This will perform the following
1. Creates a `downloads`
2. Download the latest `raspios_armhf` image
3. Enable SSH on image 
4. Generate the new 'custom' image - `xxx-armf-ssh-enabled.img`

### STEP 3
Exit from vagrant SSH.
Copy generated image to SD card - something similar to this.
```shell
sudo dd if=2022-01-28-raspios-bullseye-armhf-ssh-enabled.img of=/dev/disk2
```

## Provisioning Raspberry Pi

We use `Ansible` for this. If you don't have it on your computer, go [here](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) 
to get it done.

### STEP 1 
Goto `provision` directory & install prerequisites (one-off thing)
```shell
ansible-galaxy install -r requirements.yml
```

### STEP 2
Initialise Raspberry Pi 
```shell
ansible-playbook -i raspberrypi.local, -u pi initialise.yml -k
```

This will do the following.
1. Set locale to `en_AU.UTF-8`
2. Set timezone to `Australia/Perth`
3. Set keyboard layout to `Engilsh(Australian)`
4. Change the default `raspberrypi` as it's hostname to whatever specified in `hostname`
5. Reboot 

##### FOR DEV IMAGES ONLY
Run
```shell
ansible-playbook -i my-new-hostname.local, -u pi initialise_dev.yml -k
```

### STEP 3 
Install SSM agent
```shell
ansible-playbook -i my-new-hostname.local, -u pi ssm_agent.yml -k
```
_You don't need `-k` if you've run the `initialise_dev.yml` & provided the public key._

`copy_id` means, for each jig we are creating 1 or more "duplicate" SD cards with identical configs (including `hostname`).

But we need to be able to separately identify & manage each of those SD cards. So please keep incrementing this number, 
so that it will show-up in SSM in `hostname-copy_id` format. 

Eg: `intellisense-jig-4-2`

### STEP 4 - FOR PROD IMAGES ONLY
```shell
ansible-playbook -i my-new-hostname.local, -u pi initialise_prod.yml -k
```

### BONUS 
Make sure you label the SD cards even before you pop-in to Pi. Trust me, you won't regret.

### TROUBLESHOOTING
#### Changed host key error
Just run, 
```shell
ansible-playbook -i whatever-my-hostname, ssh_keyscan.yml
```
or
```shell
ssh-keyscan whatever-my-hostname >> ~/.ssh/known_hosts 
```

#### No SSHPASS error
If you received the following error when trying to connect to the hosts with password (with `-k`)
```shell
fatal: [raspberrypi.local]: FAILED! => {"msg": "to use the 'ssh' connection type with passwords or pkcs11_provider, you must install the sshpass program"}
```
then run the following (on Mac),
```shell
brew tap esolitos/ipa
brew install sshpass
```