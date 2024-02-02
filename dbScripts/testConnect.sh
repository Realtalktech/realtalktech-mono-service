#!/bin/bash

# Global variables
HOST="localhost"
USERNAME="user"
PASSWORD="password"
DATABASE="test_db"

# Connect to the MySQL instance
mysql -h $HOST --protocol=TCP -u $USERNAME -p$PASSWORD $DATABASE

