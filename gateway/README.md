
# gateway

The contents of this directory structure automatically provisions a Multitech Conduit gateway for use alongside a Pulse jig.

The gateway's purpose is to allow the Pulse devices to have their LoRaWAN capabilities proven in the factory.

We use the Conduit software's [commissioning](http://www.multitech.net/developer/software/mlinux/getting-started-with-conduit-mlinux/commissioning-for-mlinux-devices/) process and it's [API](http://www.multitech.net/developer/software/mtr-software/mtr-api-reference/) to complete this.

We are required to put AWS SSM Agent on the device in order to manage it remotely. There is no `armv5tejl` architecture build of it so we do it ourselves. The OS on the Conduit is not terribly mature and contains a broken python install (it misses some of stdlib!) which prevents ansible from working properly, which is why there is still manual steps. :(

## install

In order to use this repository you will need both sshpass and ansible:
- pipx install ansible
- apt install sshpass

## building

You will need to build AWS SSM Agent by doing the following:

```bash
# get the code and build the container as a once-off
git clone git@github.com:aws/amazon-ssm-agent.git
cd amazon-ssm-agent
docker build -t ssm-agent-build-image .
# build the binaries, specifically for our architecture
docker run -it --rm --name ssm-agent-build-container -v `pwd`:/amazon-ssm-agent -e GOOS=linux -e GOARCH=arm -e GO_BUILD='GOARM=5 CGO_ENABLED=0 go build -ldflags "-s -w" -trimpath' ssm-agent-build-image make -e clean pre-release build-any-arm
# copy the resultant binaries into this repo
cp -r bin/linux_arm/. ../pulse-production-jig-app/gateway/roles/jig/files/ssm/usr/bin/
```

## provisioning

Now to actually provision a Conduit perform the following steps:

1) Reset the Conduit to [factory defaults](https://www.multitech.net/developer/software/aep/reset-button-behavior-for-aep/) by holding down the reset button for 30+ seconds.
2) Configure your machine's ethernet port to accept DHCP and plug into the Conduit.
3) Execute `ansible-playbook commission.yml --extra-vars "conduit_password=<DESIRED ADMIN PASSWORD>"` and wait for completion.
4) Configure you machine's ethernet port to provide DHCP and internet connectivity and reconnect to the conduit.

Now for the manual part because Python is broken on the Conduit OS:

1) Create the SSM Hybrid agent activation:

```bash
aws ssm create-activation \
  --description "conduit ssm agent test" \
  --registration-limit 1 \
  --iam-role service-role/AmazonEC2RunCommandRoleForManagedInstances
```

2) Copy SSM agent binaries to the Conduit:

```bash
# gain the IP (10.42.0.25 here) from your DHCP logs, e.g. grep 'dnsmasq' /var/log/syslog
rsync -r -e ssh roles/jig/files/ssm admin@10.42.0.25:/tmp/ssm
```

3) Hop onto the Conduit, e.g. `ssh admin@10.42.0.25`
4) Move the files to the correct locations:

```bash
sudo mv /tmp/ssm/etc/amazon /etc
sudo mv /tmp/ssm/etc/init.d/ssm-agent /etc/init.d/ssm-agent
sudo mv /tmp/ssm/usr/bin/* /usr/bin/.
```

5) Register the device with SSM Agent and start the agent:

```bash
sudo /usr/bin/amazon-ssm-agent -register -code <CODE> -id <ID> -region ap-southeast-2
sudo /etc/init.d/ssm-agent start
```

For troubleshooting you may find logs in `/var/log/amazon/ssm`.
