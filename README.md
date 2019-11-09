# Udacity Project 2: Category Website

This project is a simple website with a functionality of logging-in via google account. The whole idea of the category website is to be able to store and do CRUD operation on the database. The category Database was aimed for the use of sport and sports items relationship.

## Installation
###### What should the have installed?
+ [Vagrant](https://www.vagrantup.com/downloads.html)
+ [Virtual Box](https://www.virtualbox.org/wiki/Downloads)
+ vagrantfile
+ python 3
+ gitbash for window users
+ catalog file(which includes)
1. templates(folder)
2. static(folder)
3. application.py
4. database_setup.py
5. README.md

###### What steps should be taken?
To run the program change directory in cmd line to virtual machine
` cd Downloads/fsnd-virtual-machine/FSND-Virtual-Machine/vagrant/catalog`

Vagrant up
`vagrant up`

log into vagrant
`vagrant ssh`

change directory to /vagrant
`cd /vagrant`

change directory to catalog
`cd catalog`

to set up database
`python database_setup.py`

to run webserver and application
`python application.py`

go to the browser and type in the link
`http://localhost:5000/catalog`

Now, enjoy playing around the with the database by adding your own sports and items.

###### Author
Jonathan Rogers
