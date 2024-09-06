Vagrant.configure("2") do |config|
    # Define the base box
    config.vm.box = "generic/ubuntu2204"
    config.vm.synced_folder ".", "/vagrant"

    config.vm.define "bot" do |bot|
        bot.vm.hostname = "bot"
        bot.vm.network "private_network", ip: "192.168.50.10"
        bot.vm.provision "shell",inline: <<-SHELL
            sudo apt-get update -y
            sudo apt-get install -y python3 python3-pip
        SHELL
    end
    config.vm.define "pg-primary" do |primary|
        primary.vm.hostname = "pg-primary"
        primary.vm.network "private_network", ip: "192.168.50.11"
        primary.vm.provision "shell",inline: <<-SHELL
            sudo apt-get update -y
            sudo apt-get install -y postgresql postgresql-contrib python3 python3-pip
            pip install psycopg2-binary
        SHELL
    end
    config.vm.define "pg-replica" do |replica|
        replica.vm.hostname = "pg-replica"
        replica.vm.network "private_network", ip: "192.168.50.12"
        replica.vm.provision "shell",inline: <<-SHELL
            sudo apt-get update -y
            sudo apt-get install -y postgresql postgresql-contrib
        SHELL
    end
    config.vm.define "ansible" do |ansible|
        ansible.vm.hostname = "ansible"
        ansible.vm.network "private_network", ip: "192.168.50.13"
        ansible.vm.provision "shell",inline: <<-SHELL
            sudo apt-get update -y
            sudo apt-get install -y  python3 python3-pip sshpass
            pip3 install ansible
        SHELL
    end

  end