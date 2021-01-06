# Deploying  SLURM in a Docker container from source
Trying to copy `agaveapi/slurm` image building instructions to Ubuntu 20.04 to deploy SLURM in the `sistr-server-dev` image.

Due to PID 1 daemon issue, the only possibility is to use `supervisord` to launch daemon
Launch docker and type `docker run -it --rm -v `pwd`:/mnt -h sistr-dev  sistr-server-dev bash`


```bash 
apt update
apt -y install gcc g++ make munge libmunge-dev bzip2 vim tar git supervisor wget openssh-server

cd /usr/local
#git clone https://github.com/SchedMD/slurm.git
#git checkout tags/slurm-20-11-2-1
wget https://github.com/SchedMD/slurm/archive/slurm-20-11-2-1.tar.gz

#compile SLURM 20.11
./configure --prefix=/usr --sysconfdir=/etc/sysconfig/slurm --with-mysql_config=/usr/local/bin
make && make install && mkdir -p /etc/sysconfig/slurm
cp etc/init.d.slurm /etc/init.d/slurmd && chmod +x /etc/init.d/slurmd

#Setup munge service
chown -R root:root /var/log/munge /var/lib/munge
mkdir -p /var/run/munge && chown -R root:root /var/run/munge /etc/munge /run/munge /var/log/munge/


#Create SLURM directories and add user SLURM
adduser slurm && echo "slurm:slurm" 
mkdir -p /var/log/slurm && touch /var/log/slurm/job_completions  /var/log/slurm/accounting
chown -R slurm:slurm /var/log/slurm
mkdir -p /var/spool/node_state /var/spool/job_state
chown -R  root:slurm /var/spool && chmod g+w /var/spool

#Create SSH directory for successul daemon launch
mkdir /run/sshd

# Copy config files to the directory
cp /mnt/slurm.conf /etc/sysconfig/slurm/slurm.conf
cp /mnt/supervisord.conf /etc/supervisord.conf
/usr/sbin/slurmctld -D -vvvvvv

# Launch services via supervisord
/usr/bin/supervisord -c /etc/supervisord.conf -s &
```
