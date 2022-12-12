# Creates a test environment, installs the requests package, and runs the monitor script.
# Begin a sidecar instance before running this script!
python -m venv test-env
. ./test-env/bin/activate
python -m pip install requests web3 substrate-interface
python monitor.py