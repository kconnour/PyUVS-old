:orphan:

These are my notes for making a database with PostgreSQL and Datagrip.

Setup PostgreSQL
----------------
Install: `sudo apt install postgresql`.
Start: `sudo su - posgres` and then `psql`.

Then we have to use it to setup a database
`create user kyle with password 'iuvs';
create database iuvs;
grant all privileges on database iuvs to kyle;
\q`.

Now we have an empty database that can be added to.

Datagrip
--------
Set the name of the "project" and login using the credentials you just
defined above. This is not a datagrip thing!
