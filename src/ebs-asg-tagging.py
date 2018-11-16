import os
import boto3
import json
import logging
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Determine the region
    region = os.environ['AWS_REGION']

    # Get a client for EC2
    client = boto3.client('ec2', region_name=region)

    # Dump the whole SNS message for posterity
    logger.info(json.dumps(event))

    # Extract the message from the SNS message
    message = event['Records'][0]['Sns']['Message']

    # Parse the JSON of the message
    asg_event = json.loads(message)

    # Get the instanceId that triggered this event
    instance_id = asg_event['EC2InstanceId']

    # Add tags for volumes upon instance termination or termination_error
    if asg_event['Event'].startswith('autoscaling:EC2_INSTANCE_TERMINATE'):
        logger.info("Dealing with a termination")

        # Find all the volumes that have the terminated instance's InstanceId tag
        filters = [
            {'Name': 'tag:InstanceId', 'Values': [instance_id]}
        ]
        result = client.describe_volumes(Filters=filters)

        for volume in result['Volumes']:
            logger.info(volume['VolumeId'] + " was attached to terminated instance " + instance_id)
            ec2 = boto3.resource('ec2')
            vol = ec2.Volume(volume['VolumeId'])

            now = datetime.datetime.now()

            tags = [
                {'Key': 'TerminationDate', 'Value': now.isoformat()}
            ]

            vol.create_tags(Tags=tags)
            log_msg("Added TerminationDate tag for volume: " + volume['VolumeId'])

    # Add tags for volumes upon instance launch or launch_error
    if asg_event['Event'].startswith('autoscaling:EC2_INSTANCE_LAUNCH'):
        logger.info("Dealing with a launch")

        # Get all the volumes for the instance
        filters = [
            {'Name': 'attachment.instance-id', 'Values': [instance_id]}
        ]
        result = client.describe_volumes(Filters=filters)

        for volume in result['Volumes']:
            logger.info(volume['VolumeId'] + " attached to new instance " + instance_id)
            ec2 = boto3.resource('ec2')
            vol = ec2.Volume(volume['VolumeId'])

            tags = [
                {'Key': 'InstanceId', 'Value': instance_id}
            ]

            vol.create_tags(Tags=tags)
            log_msg("Added InstanceId tag for volume: " + volume['VolumeId'])


def log_msg(msg):
    print msg
    logger.info(msg)
