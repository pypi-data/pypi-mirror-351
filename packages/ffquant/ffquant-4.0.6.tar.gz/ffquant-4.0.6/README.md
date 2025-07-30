# Install JupyterHub

```SHELL
curl -L https://tljh.jupyter.org/bootstrap.py | sudo -E python3 - --admin tljhadmin --version 1.0.0b1
```

Edit ~/.profile, add the following to the end

```SHELL
export PATH=/opt/tljh/user/bin/:$PATH
```

```SHELL
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
nvm install 20.17.0
nvm alias default 20.17.0
curl -fsSL https://deb.nodesource.com/setup_current.x | sudo -E bash -
sudo apt install -y nodejs
wget https://github.com/apache/rocketmq-client-cpp/releases/download/2.0.0/rocketmq-client-cpp-2.0.0.amd64.deb
sudo dpkg -i rocketmq-client-cpp-2.0.0.amd64.deb
sudo -E /opt/tljh/user/bin/python3 -m pip install backtrader matplotlib dash pandas psutil ffquant numpy confluent-kafka apollo-client boto3 pandas_market_calendars
sudo chmod -R 777 /opt/tljh/user/lib/python3.10/site-packages/pyapollo/
sudo -E /opt/tljh/user/bin/python -m pip install jupyterlab-git==0.44.0
sudo -E /opt/tljh/user/bin/jupyter lab build
sudo systemctl restart jupyterhub jupyter-tljhadmin
```

Visit http://192.168.25.144 in your browser

Log in as tljhadmin and set your password


# Let new user register with username and password
```SHELL
sudo tljh-config set auth.type nativeauthenticator.NativeAuthenticator
sudo tljh-config reload
```

BE CAREFULL!!! When this feature is enabled, the admin user has to go through the sign-up process. Username must be the same with the one used in the installation command.

Admin user authorizes user registration at http://192.168.25.144/hub/authorize

# Disable Terminal
Log in as admin. Open the terminal and execute commands:

```SHELL
jupyter notebook --generate-config
sudo mv /home/jupyter-tljhadmin/.jupyter/jupyter_notebook_config.py /opt/tljh/user/etc/jupyter/
```

Edit /opt/tljh/user/etc/jupyter/jupyter_notebook_config.py and change c.NotebookApp.terminals_enabled to False.

```SHELL
sudo systemctl restart jupyterhub jupyter-tljhadmin
```

# Disable Culling Idle Servers
```SHELL
sudo tljh-config set services.cull.max_age 0
sudo tljh-config set services.cull.timeout 31536000
sudo systemctl restart jupyterhub jupyter-tljhadmin
```

# Installing Apollo
Install Docker
```SHELL
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```
log out from the terminal and log in.

Install docker-compose
```SHELL
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Visit https://github.com/apolloconfig/apollo-quick-start and get docker-compose.yml and sql folder. Rearrange them like:
```SHELL
- docker-quick-start
  - docker-compose.yml
  - sql
    - apolloconfigdb.sql
    - apolloportaldb.sql
```
Execute ```docker-compose up``` under docker-quick-start directory

# Make backtest_data_viewer.exe
Run the following command at the root directory of ffquant on Windows.
```SHELL
python ffquant/utils/make_bt_data_viewer.py
```
Output exe file path is dist/backtest_data_viewer_1.0.0.exe

Open bt_data_viewer_setup.iss with Inno Setup and Compile. The Setup Installer is Output/mysetup.exe


# Compile ffquant and upload to PyPi
python -m pip install setuptools wheel twine

Increase version number in setup.py

python setup.py sdist bdist_wheel

python -m twine upload dist/*

Ask Joanthan for PyPi API token.


## Install Apollo Config Center

```SHELL
sudo apt update
sudo apt install openjdk-17-jdk
sudo apt install mariadb-server
sudo mysql -u root -p
```

```SQL
CREATE DATABASE ApolloPortalDB;
CREATE DATABASE ApolloConfigDB;
```

Get SQL script file:
https://github.com/apolloconfig/apollo/blob/master/scripts/sql/profiles/mysql-default/apolloconfigdb.sql
https://github.com/apolloconfig/apollo/blob/master/scripts/sql/profiles/mysql-default/apolloportaldb.sql


```SQL
source /home/sdroot/apolloportaldb.sql;
source /home/sdroot/apolloconfigdb.sql;
```

```SHELL
CREATE USER 'apollo_user'@'%' IDENTIFIED BY 'sd123456';
GRANT ALL PRIVILEGES ON ApolloConfigDB.* TO 'apollo_user'@'%';
GRANT ALL PRIVILEGES ON ApolloPortalDB.* TO 'apollo_user'@'%';
FLUSH PRIVILEGES;
```

Get three installer packages
https://github.com/apolloconfig/apollo/releases/download/v2.3.0/apollo-adminservice-2.3.0-github.zip
https://github.com/apolloconfig/apollo/releases/download/v2.3.0/apollo-configservice-2.3.0-github.zip
https://github.com/apolloconfig/apollo/releases/download/v2.3.0/apollo-portal-2.3.0-github.zip


unzip and edit each config/application-github.properties file. Fill in DB credentials.

apollo-adminservice-2.3.0-github/config/application-github.properties as follows
```
spring.datasource.url = jdbc:mysql://localhost:3306/ApolloConfigDB?characterEncoding=utf8
spring.datasource.username = apollo_user
spring.datasource.password = sd123456
```

apollo-configservice-2.3.0-github/config/application-github.properties as follows
```
spring.datasource.url = jdbc:mysql://localhost:3306/ApolloConfigDB?characterEncoding=utf8
spring.datasource.username = apollo_user
spring.datasource.password = sd123456
```

apollo-portal-2.3.0-github/config/application-github.properties as follows
```
spring.datasource.url = jdbc:mysql://localhost:3306/ApolloPortalDB?characterEncoding=utf8
spring.datasource.username = apollo_user
spring.datasource.password = sd123456
```

Edit apollo-portal-2.3.0-github/config/apollo-env.properties Replace `fill-in-dev-meta-server` with `localhost`

```SHELL
sudo mkdir /opt/logs
sudo chmod -R 777 /opt/logs
```

Execute each scripts/startup.sh to start servers.
