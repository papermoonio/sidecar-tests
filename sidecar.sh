# Starts up a Moonbase Alpha sidecar instance that's stored at ../sidecar
cd ../sidecar
export SAS_SUBSTRATE_WS_URL=wss://wss.api.moonbase.moonbeam.network
node_modules/.bin/substrate-api-sidecar 