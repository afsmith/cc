Vagrant.configure("2") do |config|

   config.vm.box = "debain-wheezy"
   config.vm.synced_folder ".", "/vagrant", :mount_options => ["dmode=777","fmode=666"] 
   config.vm.network "public_network", ip: "192.168.0.133"
   config.vm.provision :shell, :path => "bootstrap.sh"

end
