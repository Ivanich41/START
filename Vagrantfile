Vagrant.configure("2") do |config|
    config.vm.box = "generic/ubuntu2204"
    config.vm.synced_folder ".", "/vagrant"

    config.vm.define "docker" do |docker|
        docker.vm.hostname = "docker"
    
        docker.vm.network "private_network", ip: "192.168.50.10"

        docker.vm.provision "shell", inline: <<-SHELL
        # Устанавливаем docker
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
        
        # Разрешить доступ к registry
            sudo cp /vagrant/auxiliary/deamon.json /etc/docker/daemon.json
            sudo service docker restart
        SHELL
    end

    config.vm.define "registry" do |registry|
        registry.vm.hostname = "registry"
        
        registry.vm.network "private_network", ip: "192.168.50.11"
        registry.vm.provision "shell", inline: <<-SHELL
        # Устанавливаем docker
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
        # Деплоим regisrty
            sudo docker run -d -p 5000:5000 -v $HOME/registry:/var/lib/registry registry:latest
        SHELL
    end

end