import os
import boto3
import logging
import dateutil.parser

from datetime import datetime,timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Define retention period in days
    retention_days = int(os.environ['retention_days'])

    # Determine the region
    region = os.environ['AWS_REGION']

    # Get current timestamp in UTC
    now = datetime.now()

    ec2 = boto3.client('ec2', region_name=region)

    # Find all the volumes that have the terminated instance's InstanceId tag
    filters = [
        {'Name': 'tag-key', 'Values': ['TerminationDate']}
    ]
    result = ec2.describe_volumes(Filters=filters)

    for volume in result['Volumes']:
        logger.info("Evaluating " + volume['VolumeId'] + " to see if it can be deleted")
        ec2 = boto3.resource('ec2')
        vol = ec2.Volume(volume['VolumeId'])

        if vol.state == 'available':
            for tag in vol.tags:
                if tag['Key'] == 'TerminationDate':
                    # Get and parse the termination date from the tag
                    terminationDate = dateutil.parser.parse(tag.get('Value'))

                    # See if the delta between now and the termination date is greater than our retention period
                    if (now - terminationDate) > timedelta(retention_days):
                        # Delete Volume
                        logger.info("Volume " + volume['VolumeId'] + " should be deleted.")
                        vol.delete()
                        log_msg("Volume " + volume['VolumeId'] + " deleted.")
                    else:
                        log_msg("Volume " + volume['VolumeId'] + " should be retained.")
        else:
            log_msg("Volume " + volume['VolumeId'] + " is not in the correct state for deletion: " + vol.state)


def log_msg(msg):
    print msg
    logger.info(msg)
