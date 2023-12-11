#!/usr/bin/env python3

import argparse
import os
import time
from pprint import pprint

import googleapiclient.discovery
import google.auth
import google.oauth2.service_account as service_account
import numpy as np
np.linalg.qr()
#
# Stub code - just lists all instances
#
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None


def create_instance(compute, project, zone, name):
  # Borrowed and modified from https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/compute/api/create_instance.py#L58
  image_response = compute.images().getFromFamily(project='ubuntu-os-cloud', family='ubuntu-2204-lts').execute()
  source_disk_image = image_response['selfLink']
  machine_type = "zones/{}/machineTypes/e2-small".format(zone)
  startup_script = open(os.path.join(os.path.dirname(__file__), "startup_script.sh")).read()
  config = {
        "name": name,
        "machineType": machine_type,
        # Specify the boot disk and the image to use as a source.
        "disks": [
            {
                "boot": True,
                "autoDelete": True,
                "initializeParams": {
                    "sourceImage": source_disk_image,
                },
            }
        ],
        # Specify a network interface with NAT to access the public
        # internet.
        "networkInterfaces": [
            {
                "network": "global/networks/default",
                "accessConfigs": [{"type": "ONE_TO_ONE_NAT", "name": "External NAT"}],
            }
        ],
        # Allow the instance to access cloud storage and logging.
        "serviceAccounts": [
            {
                "email": "default",
                "scopes": [
                    "https://www.googleapis.com/auth/devstorage.read_write",
                    "https://www.googleapis.com/auth/logging.write",
                ],
            }
        ],
        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        "metadata": {
            "items": [
                {
                    # Startup script is automatically executed by the
                    # instance upon startup.
                    "key": "startup-script",
                    "value": startup_script,
                }
            ]
        },
    }
  return compute.instances().insert(project=project,zone=zone,body=config).execute()


def wait_for_operation(compute: object, project: str, zone: str, operation: str):
  #Borrowed and modified from https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/compute/api/create_instance.py#L174C1-L205C22
  print("Waiting for operation to finish...")
  while True:
      result = (
          compute.zoneOperations()
          .get(project=project, zone=zone, operation=operation)
          .execute()
      )

      if result["status"] == "DONE":
          print("done.")
          if "error" in result:
              raise Exception(result["error"])
          return result
      time.sleep(10)


def main(project, zone, instance_name):
    # Borrowed and modified from https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/compute/api/create_instance.py#L174C1-L205C22
    credentials = service_account.Credentials.from_service_account_file(filename='service-credentials.json')
    compute = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)

    print("Creating instance with zone {} and instance name {} inside project {}".format(zone, instance_name, project))
    operation = create_instance(compute, project, zone, instance_name)
    wait_for_operation(compute, project, zone, operation['name'])
    instances = list_instances(compute, project, zone)
    for instance in instances:
        print(' : ' + instance['name'])

    firewall_json = {
    "name": "allow-5000",
    "sourceRanges":["0.0.0.0/0"],
    "allowed": [
    {
        "IPProtocol": "tcp",
        "ports": ["5000"]
    }
    ],
    "targetTags": ["allow-5000"],
    }
    try:
        request = compute.firewalls().insert(project=project, body=firewall_json)
        response = request.execute()
        print("Firewall created successfully")
    except Exception as exp:
        print("Not creating firewall since its already present")

    request = compute.instances().get(project=project, zone=zone, instance=instance_name)
    response = request.execute()
    tags_for_vm = {"items": ["allow-5000"]}
    tags_for_vm["fingerprint"] = response["tags"]["fingerprint"]
    request = compute.instances().setTags(project=project, zone=zone, instance=instance_name, body=tags_for_vm)
    response = request.execute()

    print("Your running instances are:")
    for instance in list_instances(compute, project, zone):
        print(instance['name'])

main(project="tensile-medium-397918", zone="us-west1-a", instance_name="anirudh-creates-instance")