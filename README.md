# Sidecar Tests
Some python scripts to test the sidecar implementation for Moonbeam/Moonriver/Moonbase Alpha. All of the bash scripts are currently set to use Moonbase Alpha.  

## Contents

* `requirements.txt` has all of the required python packages, which can be installed via pip.  
* `sidecar.sh` is a bash script that can set up a Moonbase Alpha instance of sidecar.  
* `monitor.sh` is a bash script that runs the python tests. Use after running `sidecar.sh`.  

Please read instructions on [how to generate Moonbeam-specific types](https://docs.moonbeam.network/builders/substrate/libraries/sidecar/#generating-the-types-bundle){target=\_blank}.

## Run Sidecar with Docker

Launch the sidecar container connected to the network of your choice, and in the version defined. Will be listening in `localhost:8080`

```bash
RPC_ENDPOINT="wss://wss.api.moonbase.moonbeam.network"
SIDECAR_VERSION="18"

docker run -d --rm --name substrate-api-sidecar \
  -p 8080:8080 \
  -e SAS_EXPRESS_PORT="8080" \
  -e SAS_EXPRESS_BIND_HOST="0.0.0.0" \
  -e SAS_SUBSTRATE_WS_URL="${RPC_ENDPOINT}" \
  -e SAS_SUBSTRATE_URL="${RPC_ENDPOINT}" \
  --entrypoint=node \
  -t parity/substrate-api-sidecar:v${SIDECAR_VERSION}.0.0 \
  build/src/main.js
```

## Run Sidecar as an NPM Package

Please refer to the [Moonbeam Documentation](https://docs.moonbeam.network/builders/substrate/libraries/sidecar/#installing-and-running-substrate-api-sidecar){target=\_blank}.

## Sidecar tests

Launch tests with Python

```bash
python -m venv test-env
. ./test-env/bin/activate
python -m pip install requests web3 substrate-interface
# moonbase-alpha|moonriver|moonbeam
python monitor.py --network moonbase-alpha --log=INFO
```
