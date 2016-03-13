# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  # use ubuntu 14.04 as the base image
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "public_network"
  config.vm.network "forwarded_port", guest: 8888, host: 8888

  # Provider-specific configuration
  # Example for VirtualBox:
  # config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
  #   vb.memory = "1024"
  # end

  # Provision the system
  config.vm.provision "shell", inline: <<-SHELL
    # Install micropython dependencies
    add-apt-repository -y ppa:terry.guo/gcc-arm-embedded
    dpkg --add-architecture i386
    apt-get update -qq
    apt-get install -y gcc git python-pip python3 python3-dev gcc-multilib gcc-arm-none-eabi pkg-config libffi-dev libffi-dev:i386
    su vagrant -c "git clone http://github.com/micropython/micropython.git /home/vagrant/micropython"

    su vagrant -c "sudo pip install virtualenv virtualenvwrapper"

    echo "export MPUNIX=/home/vagrant/micropython/unix/micropython" >> /home/vagrant/.bashrc
    echo "PATH=/home/vagrant/micropython/unix:$PATH" >> /home/vagrant/.bashrc
    echo "export WORKON_HOME=/home/vagrant/.virtualenvs" >> /home/vagrant/.bashrc
    su vagrant -c "mkdir -p /home/vagrant/.virtualenvs"
    echo "source /usr/local/bin/virtualenvwrapper.sh" >> /home/vagrant/.bashrc

    # Install micropython
    pushd /home/vagrant/micropython
    make -C unix
    popd

    # Install mpkernel (placed in the /vagrant directory)
    pushd /vagrant
    # Create the virutalenv and build mpkernel
    su vagrant -c "source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv -p python3.4 mpkernel; pip install -r requirements.txt; make install"
    popd
  SHELL
end
