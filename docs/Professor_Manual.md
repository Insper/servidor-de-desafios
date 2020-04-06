# Professor Manual

A quick guide to teach the professors of the course how to use the system. 
It's quite simple once there are only two main actions you can do as a 
professor. Let's take a look on them.

## Add new users

To add new users you must edit the file "users.csv" withe the format below:

    username,usertype

The password will be a MD5 hash of the username, and after the student login he can change
his password if he wants to. To add the users after editing the file above, just run:

    $ python adduser.py
