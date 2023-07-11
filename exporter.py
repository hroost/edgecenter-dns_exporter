# -*- encoding: utf-8 -*-
#
# pip install requests
# pip install prometheus_client
#

from prometheus_client import start_http_server
from prometheus_client import Gauge
from prometheus_client import REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR

import time
import os
import sys
import requests
import datetime

# -------------------------------------------------------
# Get zones list
# -------------------------------------------------------
def getZones():
  try:
    r = requests.get(dns_api_url + '/zones?limit=' + str(dns_api_zones_limit), headers=headers, timeout=5)
    return r.json()
  except Exception as e:
    sys.stderr.write('error:'+str(e))
    exit(1)

# -------------------------------------------------------
# Get zone stats
# -------------------------------------------------------
def getZoneStats(zones, dt_from, dt_to):
  sys.stdout.write('Zones count: ' + str(zones['total_amount']) + ' [limit: ' + str(dns_api_zones_limit)+ ']\n')

  for zone in zones['zones']:
    # Avoid rate limiting. See https://apidocs.edgecenter.ru/cdn#section/Overview
    time.sleep(0.5)
    zone = zone['name']
    try:
      params = {
        'granularity': '1h',
        'from': dt_from,
        'to': dt_to
        }
      r = requests.get(dns_api_url + '/zones/' + zone + '/statistics', params=params, headers=headers, timeout=5)
      zone_stats_total = r.json()['total']
      sys.stdout.write('* zone: ' + str(zone) + ' Reqs: ' + str(zone_stats_total) + '\n')
      GaugeZoneStats.labels(zone).set(zone_stats_total)
    except Exception as e:
      sys.stderr.write('error:'+str(e))
      exit(1)

# -------------------------------------------------------
# Get all zones stats
# -------------------------------------------------------
def getAllZonesStats(dt_from, dt_to):
  try:
    params = {
      'granularity': '1h',
      'from': dt_from,
      'to': dt_to
      }
    r = requests.get(dns_api_url + '/zones/all/statistics', params=params, headers=headers, timeout=5)
    zones_stats_total = r.json()['total']
    sys.stdout.write('All zones requests since midnight: ' + str(zones_stats_total) + '\n')
    GaugeAllZonesStats.set(zones_stats_total)
  except Exception as e:
    sys.stderr.write('error:'+str(e))
    exit(1)


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
def main():

  # Start up the server to expose the metrics.
  start_http_server(port)

  # Generate some requests.
  while True:
      zones = getZones()
      # Reset per zone metrics
      GaugeZoneStats.clear()
      dt_from = int(datetime.datetime.combine(datetime.datetime.today(), datetime.time.min).timestamp()) # timestamp of today midnight
      dt_to = int(datetime.datetime.now().timestamp()) # timestamp now
      getAllZonesStats(dt_from, dt_to)
      getZoneStats(zones, dt_from, dt_to)
      time.sleep(interval)

# -------------------------------------------------------
# RUN
# -------------------------------------------------------

# http port - default 9886
port = int(os.getenv('PORT', 9886))

# Refresh interval between collects in seconds - default 300
interval = int(os.getenv('INTERVAL', 300))

dns_api_url = os.getenv('EDGECENTER_DNS_API_URL', 'https://api.edgecenter.ru/dns/v2')
dns_api_key = os.getenv('EDGECENTER_DNS_API_KEY', None)
# Amount of zones for getZones() - default 999
dns_api_zones_limit = int(os.getenv('EDGECENTER_DNS_API_ZONES_LIMIT', 999))

if not dns_api_key:
  sys.stderr.write("Application key is required please set EDGECENTER_DNS_API_KEY environment variable.\n")
  exit(1)

headers = {'Authorization':'APIKey ' + dns_api_key}

# Show init parameters
sys.stdout.write('----------------------\n')
sys.stdout.write('Init parameters\n')
sys.stdout.write('port: ' + str(port) + '\n')
sys.stdout.write('interval: ' + str(interval) + 's\n')
sys.stdout.write('----------------------\n')

# Disable default python metrics
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)

# Create gauge
GaugeZoneStats = Gauge('edgecenter_dns_zone_requests_today', 'Amount of requests per zone since midnight', ['zone'])
GaugeAllZonesStats = Gauge('edgecenter_dns_all_zones_requests_today', 'Amount of requests from all zones since midnight')

if __name__ == '__main__':
  main()
