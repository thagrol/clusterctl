Installation
============

Assumptions
-----------

1. Raspbian images have been downloaded and written to SD cards.
2. All steps will be performed by the user "pi".
3. Any paths written below as "/path/to/" must be changed to reflect the actual paths used on your system.
4. "Master" refers to the pi A+/B+/2/3 on which the clusterhat is mounted.
5. "Slave" refers to a connected Pi Zero.
6. Although configuration of the master may be done with a keyboard and monitor directly connected, this guide assumes it will be done over ssh.
7. The master is connected to the internet.

Prepare SD Cards
----------------
On all SD cards (for master and all slaves) enable ssh:
+ Prior to first boot create an empty file called "ssh" in the boot partition.

Master
------
1. Boot the master
2. Login as pi
3. Generate ssh keys:
```
ssh-keygen -t rsa
```
  + Accept the default for "Enter file in which to save the key "
  + **Do not** enter a passphrase when prompted.
4. Install dependencies:
```
sudo apt install python-pip python-gpiozero
```
5. Download the clusterctl files:
```
sudo apt install git
git clone https://github.com/thagrol/clusterctl
```
  or
```
wget https://raw.githubusercontent.com/thagrol/clusterctl/master/clusterctl.py
chmod a+x clusterctl.py
wget https://raw.githubusercontent.com/thagrol/clusterctl/master/gpiosetup.sh
chmod a+x gpiosetup.sh
```
6. Set gpiosetup.sh to run at every boot:
```
sudo nano /etc/rc.local
```
    + add `/path/to/gpiosetup.sh &` immediately above the line `exit(0)`.
    + save and exit rc.local
7. Power off the master:
```
sudo poweroff
```
8. Disconnect power.
9. If not already connected, attach clusterhat and pi zero(s).
10. Reconnect power and boot master.
11. Login to master as pi.

Slave(s)
--------
These steps need to be repeated for each slave pi. To avoid problems caused by an inadequate PSU, only one slave is powered up at a time.
Change host names and numbers below as needed
1. Power up the slave:
```
/path/to/clusterctl.py -n 1 on
```
2. Connect to slave via ssh:
```
ssh p1.local
```
If prompted to save keys, answer yes.
3. Generate ssh keys:
```
ssh-keygen -t rsa
```
  + Accept the default for "Enter file in which to save the key "
  + **Do not** enter a passphrase when prompted.
4. Copy the master's public key:
```
scp pi@controller.local:/home/pi/.ssh/idras.pub ~/.ssh/authorized_keys
```
5. Log out.
6. Power off the slave. On the master:
```
/path/to/clusterctl.py -n 1 stop
```