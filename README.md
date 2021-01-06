# SISTR website main repository
This repository contains full information on SISTR front and back-end deployment on server or docker container.


## Requirements
The hosting machine or docker image should have installed
1. SLURM scheduler
1. Mail server
```bash
https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-postfix-as-a-send-only-smtp-server-on-ubuntu-14-04
apt-get install mailutils
vi /etc/postfix/main.cf
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = loopback-only
service postfix restart
```
1. SISTR
```
apt install ncbi-blast++ mafft libcurl4-openssl-dev libssl-dev
pip install pandas sistr_cmd 
```
1. Web-server


## Development in docker image
The development system consists of docker image `sistr-server-dev` with all installed requirements.
Mount all directories that you require and expose port 5010 communication with Flask web-development server.
Modification of web-server files will automatically re-launch Flask web-server

```bash
#Launch docker image and mount development directories
cd ~/WORK/SISTR/SISTR-website-dev
docker run -it --rm -h sistr-dev -p 5010:5010  -v  `pwd`:/mnt sistr-server-dev:latest  bash
# Launch SLURM
/usr/bin/supervisord -c /etc/supervisord.conf -s &
# Test SLURM
sinfo && srun --cpus-per-task 1 --mem-per-cpu=1gb  date && sleep 10

# To commit changes to image
docker commit 3c62443c49ec sistr-server-dev:latest

```
