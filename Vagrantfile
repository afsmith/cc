Vagrant.configure("2") do |config|

   config.vm.box = "debain-wheezy"
   config.vm.network "public_network", ip: "192.168.0.133"
   config.vm.provision :shell, :path => "bootstrap.sh"

end
