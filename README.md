Test_bench guide
================

Description
-----------
To do

Path
----
* **/rpi_bench/libs/** : all libs for **test_bench**.
* **/rpi_bench/test_api/** : tests on api
* **/rpi_bench/test_collections/** : folder containing all the tests available on Jira.
* **/tests/** : folder with all unit tests and reporting of **rpi_bench**.

# Use Test_bench
- Go to : https://jenkins.tooling.prod.cdsf.io/job/KaaS/view/QA/
- Select a node.
- You can run with parameters


# Test local code
## Setup for rpi_bench lib testing :
You need  :
* python >= 3.9 
* tox (pip install tox)

## Run all tests + linter :
```bash
tox -c .\tox_rpi_bench.ini
```
## Run tests on specific target :
```bash
tox -c .\tox_rpi_bench.ini -e py39
```
(you can change with **py39** / **py310** / **py311**)

## Run linter :
```bash
tox -c .\tox_rpi_bench.ini -e pylint
```

# Reporting :
* **/tests/reports/ < python version > /pytest.html**
* **/tests/reports/ < python version > /coverage/index.html**
* **/tests/reports/pylint.json**
* **/tests/reports/pylint.html**

