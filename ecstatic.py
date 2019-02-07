#!/usr/bin/env python

import os
import json
import logging
import requests
import sys

import boto3
import botocore

from pprint import pformat
from dotenv import load_dotenv

load_dotenv()

ecs = boto3.client('ecs')

#
# setup logger
#

logging.basicConfig()

logger = logging.getLogger( __name__ )
logger.setLevel( os.getenv( 'ECSTATIC_LOG_LEVEL', 'INFO' ) )

logger.info( 'logger level set to {}'
  .format( logging.getLevelName( logger.getEffectiveLevel() ) )
)

#
# functions
#

def update_all_clusters():
  for c in ecs.list_clusters().get('clusterArns'):
    update_cluster_agents( [ c ] )
  return


def update_cluster_agents( clusters ):

  dc = ecs.describe_clusters(
    clusters = clusters,
    include  = [ 'TAGS' ]
  )

  for cluster in dc.get('clusters'):

    cluster_arn   = cluster.get('clusterArn')
    cluster_name  = cluster.get('clusterName')

    logger.info(
      'checking cluster, arn: {}'
        .format( cluster_arn )
    )

    lci = ecs.list_container_instances(
      cluster = cluster_arn
    )

    cia = lci.get('containerInstanceArns')

    if not cia:
      logger.info(
        'skipping cluster, no containers instances, arn: {}'
          .format( cluster_arn )
      )
      continue

    dci = ecs.describe_container_instances(
      cluster = cluster_arn,
      containerInstances = cia
    )

    # if this changes to false, then update requests will not be made for the cluster
    cluster_healthy = True

    for ci in dci.get('containerInstances'):

      ec2_instance_id = ci.get('ec2InstanceId')

      if ci.get('agentConnected') == 'False' :
        logger.warning(
          'agent is not connected, ec2_instance_id: {} {}'
            .format( ec2_instance_id, pformat( ci ) )
        )
        send_message_to_slack(
          ':boom: *agent is not connected*, ec2_instance_id: {}, cluster_arn: {}'
            .format( ec2_instance_id, cluster_arn )
        )
        cluster_healthy = False
        continue

      if ci.get('agentUpdateStatus') == 'FAILED' :
        logger.warning(
          'agent update failed, ec2_instance_id: {} {}'
            .format( ec2_instance_id, pformat( ci ) )
        )
        send_message_to_slack(
          ':boom: *agent update failed*, ec2_instance_id: {}, cluster_arn: {}'
            .format( ec2_instance_id, cluster_arn )
        )
        cluster_healthy = False
        continue

    # if the cluster has unhealthy instances, then skip update requests
    if not cluster_healthy:
      logger.warning(
        'skipping updates, cluster has unhealthy instances, ec2_instance_id: {}, cluster_arn: {}'
          .format( ec2_instance_id, cluster_arn )
      )
      return

    # request agent updates
    for ci in dci.get('containerInstances'):

      ec2_instance_id = ci.get('ec2InstanceId')

      containter_arn = ci.get('containerInstanceArn')
      agent_version  = ci.get('versionInfo').get('agentVersion')
      docker_version = ci.get('versionInfo').get('dockerVersion')

      try:
        logger.info(
          'attempting container agent update, cluster_name: {}, ec2_instance_id: {}'
            .format( cluster_name, ec2_instance_id, pformat( ci ) )
        )

        ecs.update_container_agent(
          cluster = cluster_arn,
          containerInstance = containter_arn
        )

        logger.info(
          'agent update requested, delaying additional updates until next run, ec2_instance_id: {}, cluster_name: {}'
            .format( ec2_instance_id, cluster_name )
        )
        logger.debug( 'agent update requested, ci: {}'.format( pformat( ci ) ) )

        send_message_to_slack(
          'agent update requested, delaying additional updates until next run, ec2_instance_id: {}, cluster_arn: {}'
            .format( ec2_instance_id, cluster_arn )
        )

        return

      except ecs.exceptions.UpdateInProgressException as err:
        logger.info( 'agent update in progress, ec2_instance_id:', ec2_instance_id )
        continue

      except ecs.exceptions.NoUpdateAvailableException as err:
        logger.info(
          'agent is current, ec2_instance_id: {}, agent_version: {}, docker_version: {}'
            .format( ec2_instance_id, agent_version, docker_version )
        )
        continue

      except Exception as e:
        logger.error(
          '! unexpected error: {} {}'
            .format( sys.exc_info()[0], pformat( e ) )
        )


def send_message_to_slack( message ):

  webhook_url = os.getenv( 'ECSTATIC_WEBHOOK_URL' )

  if not webhook_url:
    logger.info( 'skipping slack notification, ECSTATIC_WEBHOOK_URL is undefined' )
    return

  logger.debug(
    'sending message to slack, ECSTATIC_WEBHOOK_URL: {}'
      .format( webhook_url )
  )

  slack_data = { 'text': '@ecstatic: {}'.format( message ) }

  response = requests.post(
    webhook_url, data=json.dumps( slack_data ),
    headers = { 'Content-Type': 'application/json' }
  )

  if response.status_code != 200:
    logger.warn(
      'Request to slack returned an error, status_code: {}, text: {}'
        .format( response.status_code, response.text )
    )


#
# lambda handler
#

def lambda_handler( event, context ):
  update_all_clusters()
  return { 'message' : 'success' }

#
# main
#

def main():
  update_all_clusters()

if __name__ == "__main__":
  main()
