#!flask/bin/python
# This script deletes all database instances and migration records before creating it from scratch again.
# The purpose is to allow for quick setup of the DB tables based on modified models, 
# without having to worry about potential migration issues.
from subprocess import call
call(["rm", "-r", "./app.db"]) 
call(["rm", "-rf", "./db_repository"]) 
call(["./db_create.py"]) 
#call(["./db_seed.py"]) #seed db again
