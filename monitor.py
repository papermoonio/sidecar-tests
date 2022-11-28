#!/usr/bin/env python3

import requests, random, time, logging, argparse, sys
from web3 import Web3

def parse_arguments():
  parser = argparse.ArgumentParser(description="Script to test a Sidecar instance")
  parser.add_argument("-n",  "--network", required = False,
    help    = "Chain to which the sidecar instance is connected to",
    default = "moonbase-alpha"
  )
  parser.add_argument("-s", "--sidecar_endpoint", required = False,
    help    = "REST endpoint to the sidecar instance",
    default = "http://localhost:8080"
  )
  parser.add_argument("-l", "--log_level", required = False,
    help    = "Log verbosity level for the monitor",
    default = "info"
  )

  # Parse script arguments
  args = parser.parse_args()
  return args

def fetch_sidecar_api(api_path, retries = 5):
  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
  url = f"{args.sidecar_endpoint}{api_path}"
  response = None
  error = None

  for retry in range(retries):
    if retry > 0:
      time.sleep(2)
    logger.debug(f"Sending API call to sidecar endpoint ({url}) - Try #{retry}")

    try:
      response = requests.get(url, headers = headers)

      # If we come to this point, we're good to go and stop retrying
      logger.debug(f"Successfully fetched data from endpoint")
      error = None
      break
    except Exception as e:
      logger.debug(f"Could not fetch data from endpoint, will retry. Error: {e}")
      error = e

  return response, error

def perform_api_test(test_name, api_path):
  logger.info(f"=========================================================")
  logger.info(f"Test: {test_name}, Path: {api_path}")
  response, error = fetch_sidecar_api(api_path)

  if error is not None:
    logger.error(f"  [✘] Test failed - Error: {error}")
    return False

  if response.status_code != requests.codes.ok:
    logger.error(f"  [✘] Test failed - Error: Unexpected status code {response.status_code}")
    return False

  logger.info(f"  [✔] Test passed - Took {response.elapsed.total_seconds() * 1000:.2f}ms")
  logger.debug(f"      Detailed response: {response.json()}")

  return True

# TODO: fetch from sidecar
# TODO: fetch from polkadot
# TODO: fetch from rpc? might be too much testing
def perform_content_test():
  w3 = Web3(Web3.HTTPProvider(rpc_url[args.network]))
  response, error = fetch_sidecar_api("/blocks/head")

  resjson = response.json()
  blockNum = resjson['number']
  extrinsics = resjson['extrinsics']

  for extr in extrinsics:
    method = extr['method']
    if(method['pallet'] == 'ethereum' and method['method'] == 'transact'):
      # logger.info(extr)
      tx = extr['args']['transaction']

      if('legacy' in tx):
        logger.info('Legacy found!')
        #logger.info(tx)
      elif('eip1559' in tx):
        logger.info('EIP-1559 found!')

        # Get relevant data to calculate the gas price
        maxPriorityFeePerGas = int(tx['eip1559']['maxPriorityFeePerGas'])
        maxFeePerGas = int(tx['eip1559']['maxFeePerGas'])
        baseGasFee = base_fee[args.network]

        # Calculate the gas price
        gasPrice = baseGasFee + maxPriorityFeePerGas if (baseGasFee + maxPriorityFeePerGas < maxFeePerGas) else maxFeePerGas

        # Get the weight
        try:
          # Try to get weight from the extrinsic events
          if(len(extr['events']) > 1):
            finalEvent = extr['events'][-1]
            #logger.info(finalEvent)
            if(finalEvent['method']['method'] == 'ExtrinsicSuccess'):
              weight = int(finalEvent['data'][0]['weight']['refTime'])
            else:
              raise Exception("The final event was not 'ExtrinsicSuccess'")

            transactionHash = extr['events'][-2]['data'][2]
          else:
            raise Exception("There were no events in the final event of the extrinsic.")

          # Log out the weight & other data
          logger.info("ethereum transaction hash: " + transactionHash)
          logger.info("weight: " + str(weight))
          logger.info("adjusted weight: " + str(weight + base_extrinsic_weight[args.network]))
          logger.info("Gas price: " + str(gasPrice))
          logger.info("max fee per gas: " + str(maxFeePerGas))
          logger.info("max priority fee per gas: " + str(maxPriorityFeePerGas))
          logger.info("base gas fee: " + str(baseGasFee))

          # Calculate transaction fee
          transactionFee = (gasPrice * (weight + base_extrinsic_weight[args.network])) / 2500
          logger.info("Transaction Fee: " + str(transactionFee))       
        except:
          logger.info("###### ERROR DURING SIDECAR CALCULATION ######")

        txData = w3.eth.get_transaction(transactionHash)
        logger.info("WEB3 GAS: " + str(txData['gas']))
        logger.info("WEB3 GASPRICE: " + str(txData['gasPrice']))
        logger.info("WEB3 MAXFEEPERGAS: " + str(txData['maxFeePerGas']))
        logger.info("WEB3 MAXTIPPERGAS: " + str(txData['maxPriorityFeePerGas']))

      elif('eip2930' in tx):
        logger.info('EIP-2930 found!')  


def main(amount_random_blocks = 10):
  # tests = [
  #   {"test_name": "Fetch node version", "api_path": "/node/version"},
  #   {"test_name": "Fetch runtime spec", "api_path": "/runtime/spec"},
  #   {"test_name": "Fetch latest (best) block", "api_path": "/blocks/head"},
  #   {"test_name": "Fetch latest (best) block header", "api_path": "/blocks/head/header"},
  # ]

  # for b in problematic_blocks[args.network]:
  #   tests.append({"test_name": f"Fetch problematic block #{b}", "api_path": f"/blocks/{b}"})

  # for test in tests:
  #   test_passed = perform_api_test(*test.values())
  #   if not test_passed:
  #     sys.exit(1)

  # # Fetch first block of the latest runtime
  # response, error = fetch_sidecar_api("/runtime/spec")
  # if error or response.status_code != requests.codes.ok:
  #   logger.critical("Could not fetch the first block of the last runtime")
  #   sys.exit(1)

  # first_block_of_runtime = int(response.json()["at"]["height"])

  # tests = []
  # for _ in range(amount_random_blocks):
  #   random_block = random.randint(1, first_block_of_runtime)
  #   tests.append({"test_name": f"Fetch random block #{random_block}", "api_path": f"/blocks/{random_block}"})

  # # Tests to ensure that the endpoints have no errors
  # for test in tests:
  #   test_passed = perform_api_test(*test.values())
  #   if not test_passed:
  #     sys.exit(1)

  # Tests to ensure that the content of the blocks have no errors
  perform_content_test()

if __name__ == "__main__":
  # Set a logger for the app
  logging.basicConfig(
    format  = '%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S',
    level   = logging.INFO,
  )
  logger = logging.getLogger(__name__)

  # Get args from invocation
  args = parse_arguments()

  # Set logger verbosity
  log_levels = { "debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING, "error": logging.ERROR }
  logger.setLevel(log_levels.get(str(args.log_level).lower(), logging.INFO))

  # Dictionary containing known problematic blocks that should be checked, specific to Moonbeam networks
  problematic_blocks = {
    'moonbase-alpha': [6600, 6601],
    'moonriver': [],
    'moonbeam': [],
  }

  # Dictionary containing the base gas fee for transactions, specific to Moonbeam networks
  base_fee = {
    'moonbase-alpha': 1000000000,
    'moonriver': 1000000000,
    'moonbeam': 100000000000,
  }

  # Dictionary containing base extrinsic weight
  base_extrinsic_weight = {
    'moonbase-alpha': 250000000,
    'moonriver': 86298000,
    'moonbeam': 86298000,
  }

  # Dictionary containing RPC URLs
  rpc_url = {
    'moonbase-alpha': 'https://moonbase-alpha.public.blastapi.io',
    'moonriver': 'https://moonriver.public.blastapi.io',
    'moonbeam': 'https://moonbeam.public.blastapi.io',
  }
  
  main()
