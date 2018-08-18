#!/bin/bash

# This script runs all the test modules
cd test_modules
/home/oli/virtualenvs/standard_python3.5/bin/python3.5 test_Karr2012Bc3.py
/home/oli/virtualenvs/standard_python3.5/bin/python3.5 test_Karr2012Bg.py
/home/oli/virtualenvs/standard_python3.5/bin/python3.5 test_Karr2012_bc3_job_submissions.py
#/home/oli/virtualenvs/standard_python3.5/bin/python3.5  -m unittest discover
cd ..
