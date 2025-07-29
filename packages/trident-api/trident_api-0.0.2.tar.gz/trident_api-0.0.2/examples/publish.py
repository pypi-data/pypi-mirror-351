import os
import argparse
import logging
import time
from dotenv import load_dotenv
from logging import basicConfig, getLogger, Logger

from trident_api import TridentClient


logger = getLogger(__name__)

def init_logger(log_level: int) -> Logger:
  basicConfig(level=log_level, style="{", format="{asctime} {levelname:7} {message}")
  return getLogger(__name__)

def init_argparse():
  parser = argparse.ArgumentParser(description="Trident Client.")
  parser.add_argument(
    '--log',
    default='WARNING',
    help='Set the logging level. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL'
  )
  parser.add_argument(
    '--env',
    default='.env',
    help='Set the environment file path.'
  )
  return parser.parse_args()

def init_dotenv(env_file='.env'):
  if os.path.exists(env_file):
    load_dotenv()
    logger.info(f"Loaded environment variables from {env_file}")
  else:
    logger.warning(f"{env_file} not found; skipping loading of environment variables")

algorithm = {
  "name": "Trident Algorithm Asset",
  "description": "# Trident Algorithm \n\n![Trident Banner](https://iot.ift.tuwien.ac.at/trident/trident_banner_long.png)\n\nThis algorithm has been published using the trident service by TU Wien.",
  "author": "IFT - TU Wien",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "timeout": 3600,
  "datatokenName": "Compute Access Token",
  "datatokenSymbol": "CAT",
  "pricing": "FIXED_EUROE",
  "method": "GET",
  "url": "https://raw.githubusercontent.com/deltaDAO/nautilus-examples/main/example_publish_assets/count-lines-algorithm.js",
  "language": "Node.js",
  "version": "1.0.0",
  "entrypoint": "node $ALGO",
  "image": "node",
  "tag": "18.17.1",
  "checksum": "sha256:91e37377b960d0b15d3c15d15321084163bc8d950e14f77bbc84ab23cf3d6da7"
}

asset = {
  "name": "Trident Dataset Asset",
  "description": "# Trident Dataset Asset \n\n![Trident Banner](https://iot.ift.tuwien.ac.at/trident/trident_banner_long.png)\n\nThis asset has been published using the [Trident Service](https://iot.ift.tuwien.ac.at/trident/api) by TU Wien. You can authenticate [here](https://iot.ift.tuwien.ac.at/trident/).",
  "author": "IFT - TU Wien",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "timeout": 3600,
  "datatokenName": "Compute Access Token",
  "datatokenSymbol": "CAT",
  "pricing": "FIXED_EUROE",
  "method": "GET",
  "url": "https://raw.githubusercontent.com/deltaDAO/nautilus-examples/main/example_publish_assets/example-dataset.json",
  "trustedAlgorithms": []
}

if __name__ == "__main__":
  args = init_argparse()
  log_level = os.getenv("LOG_LEVEL") or args.log.upper()
  init_logger(getattr(logging, log_level, logging.WARNING))
  init_dotenv(args.env)
  
  skip = True # this is hardcoded to skip creation and deletion of new assets...

  trident_service = os.getenv('TRIDENT_SERVICE')
  trident_username = os.getenv('TRIDENT_USERNAME')
  trident_password = os.getenv('TRIDENT_PASSWORD')
  client = TridentClient(trident_service, trident_username, trident_password)
  
  logger.info(f"See service description {trident_service}/api")
  
  if not skip:
    logger.info(f"POST algorithm to trident...")
    response = client.post('/nautilus/algorithm/compute', algorithm)
    algorithm_did = response.json()["ddo"]["id"]
    logger.info(f"Created algorithm with did {algorithm_did}")

    logger.info("Waiting 60 seconds... meanwhile check https://flex4res.pontus-x.eu/search?sort=nft.created&sortOrder=desc")
    time.sleep(60)
    
    logger.info(f"POST asset to trident...")
    asset["trustedAlgorithms"].append(algorithm_did)
    response = client.post('/nautilus/dataset/compute', asset)
    asset_did = response.json()["ddo"]["id"]
    logger.info(f"Created asset with did {asset_did}")

    logger.info("Waiting 60 seconds... meanwhile check https://flex4res.pontus-x.eu/search?sort=nft.created&sortOrder=desc")
    time.sleep(60)
  else:
    logger.info(f"SKIPPING Publishing")
    algorithm_did = "did:op:9e33d14f295f4b0daa63f62f304d830a6a29d521e6ec436c19044307ad45ba5f"
    asset_did = "did:op:b60c770939c390dd3eee9199e968d307037765b5cc4588ced288d875195b39be"
    
  logger.info(f"POST start compute on dataset {asset_did} with algorithm {asset_did}")
  response = client.post('/nautilus/compute', { "assetDid": asset_did, "algorithmDid": algorithm_did })
  res = response.json()
  job_id = res["jobId"]
  logger.info(f"Startet compute job {job_id} with status '{res["statusText"]}'...")
  # {'agreementId': '0xb5f5f527be13ec96d1f88b4bf0f5d3a5cfe662c98d32a7d21f00f08cf97273eb', 'jobId': 'ec140dbaa10343339154be4b86e9b795', 'owner': '0xBA87B2E7F71013Fe6561a877928EA265531B06d1', 'status': 1, 'statusText': 'Warming up', 'dateCreated': '1744112400.6199', 'dateFinished': None, 'results': '', 'stopreq': 0, 'removed': 0, 'algoDID': 'did:op:b095564cbd9c5cea7253b97785add613fa86dd032eda253327b746cc65273a24', 'inputDID': ['did:op:87ec1d3294bd44ac7e889b72e043f71ee67f6781ec1ed2c1728034dbe604528e']}

  status = 0
  while status < 70:
    time.sleep(10)
    response = client.get('/nautilus/compute/status', { "jobId": job_id })
    res = response.json()
    status = res["status"]
    logger.info(f"Status {status} '{res["statusText"]}'...")
    # {'agreementId': '0x01885773e321c6ad4daf1ce966a256a974b30cf1e99138c42085c96567a46f86', 'jobId': 'c7f2c760d3a441f4bc21779849adf1bb', 'owner': '0xBA87B2E7F71013Fe6561a877928EA265531B06d1', 'status': 20, 'statusText': 'Configuring volumes', 'dateCreated': '1744125284.41753', 'dateFinished': None, 'results': '', 'stopreq': 0, 'removed': 0, 'algoDID': 'did:op:9e33d14f295f4b0daa63f62f304d830a6a29d521e6ec436c19044307ad45ba5f', 'inputDID': ['did:op:b60c770939c390dd3eee9199e968d307037765b5cc4588ced288d875195b39be']}

  if status == 70:
    response = client.get('/nautilus/compute/result', { "jobId": job_id })
    url = response.text
    logger.info(f"Result: {url}")

  if not skip:
    response = client.delete('/nautilus/delete', {"did": algorithm_did})
    logger.info(f"Deleted algorithm with did {algorithm_did}")
    
    response = client.delete('/nautilus/delete', {"did": asset_did})
    logger.info(f"Deleted asset with did {asset_did}")
