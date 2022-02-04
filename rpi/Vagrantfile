# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
 
  config.vm.box = "ubuntu/focal64"

  # Disable default sync & Sync other folders
  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.synced_folder "base_image", "/home/vagrant/base_image", create:true

  # Explicitly adding private network
  # config.vm.network "private_network", ip: "172.30.1.5"

  # Install vagrant-vbguest plugin
  # config.vagrant.plugins = "vagrant-vbguest"

  # Enable provisioning with a shell script. 
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y kpartx kmod p7zip-full
  SHELL

  # Post boot message
  $msg = <<-MSG
  ---------------------------
        IT'S RUNNING!!!                     
  ---------------------------
  MSG
  config.vm.post_up_message = $msg

end
