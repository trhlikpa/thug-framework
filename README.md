# Thug-framework
Framework for automated website checking with client honeypot Thug.
# Honeypot Thug
Thug is a client honeypot that emulates a web browser in order to detect malicious websites.

Please refer to https://github.com/buffer/thug for more information
# Installation
In order to run Thug-framework it's required to have Docker and Docker-compose installed.

Firstly clone this repository onto your system.
```
git clone https://github.com/trhlikpa/thug-framework.git
```
Once you've cloned the project to your system navigate to the directory with the project. Run the following command from this directory.
```
docker-compose up
```
This command will build and link containers based on definition located inside the docker-compose.yml file. After successful build connect to a web interface on a port (default is 5000) specified inside the docker-compose.yml file.
# Scaling
Thug-framework supports concurrent run of multiple Thug instances. Run the following command to scale up to a desired number of instances.
```
docker-compose scale worker=5
```
# License
Thug-framework is licensed under GNU General Public License v2.0
