To run the framework, you must first set up a virtual environment 

Install python3 globally: 

   apt-get install python3

Install virtualenv globally:  

   pip install virtualenv

Create virtualenv in project directory:  

   virtualenv -p <path to python3> autoapi_env

You will find that an autoapi_env directory has appears in the project root directory

Actviate the virutal env: 

   source autoapi_env/bin/activate

your unix prompt will change to reflect that you are now running inside the virtual environment.  Actually,
what has happend is that all of the environment variables in your terminal now point to the python3 instance
inside the virtual env - along with all the python tools - like pip.  

Your prompt will look like this:

   (autoapi_env)rkaye@ubuntu:~/GitMigration/cm-python-autotest$ 

Now install all project dependancies:

   pip install -r requirements.txt 

The dependancies will be installed into the virtualenv directory for this project.

To run tests - set the Content Manager URL, username and password in the config/testconfig file

  [login]
  baseurl = http://192.168.126.140:8080/ContentManager
  username = administrator
  password = scala123
  player_username = player_TABN
  player_password = 12345678
  
  [player]
  player_id = <the player id of a working player with a heartbeat>

Then run:

  nosetests tests
