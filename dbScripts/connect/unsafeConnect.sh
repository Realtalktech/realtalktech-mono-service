#!/bin/bash

# Global variables
RDS_ENDPOINT="realtalktechrdsstack-realtalktechdbinstance-c7ciisdczocf.cnqm62ueodz0.us-east-1.rds.amazonaws.com"
USERNAME="admin"
PASSWORD="ReallyRealAboutTech123!"

# Connect to the RDS instance
mysql -h $RDS_ENDPOINT -u $USERNAME -p$PASSWORD
