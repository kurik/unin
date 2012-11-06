The systemd configfiles
=======================
yaws.service - the config to start YAWS
ssh-tunel.service - setup SSH tunel to a host behind NAT

How to apply the configs
========================
1. Copy the config file to /etc/systemd/user
2. Run the following command to let systemd know about it
	# systemctl reenable /etc/systemd/user/yaws.service 
3. Start the service
	# systemctl start yaws.service

