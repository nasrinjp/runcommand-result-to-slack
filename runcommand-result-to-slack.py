from logging import getLogger, INFO
import boto3
import os
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from base64 import b64decode

logger = getLogger()
logger.setLevel(INFO)

ec2 = boto3.resource('ec2')


def decrypt_text_by_kms(encrypted_text):
    return boto3.client('kms').decrypt(CiphertextBlob=b64decode(encrypted_text))['Plaintext'].decode('utf-8')


def notify_slack(title, command_id, instance_id, instance_name, status, requested_date_time, finish_time, color):
    slack_url = decrypt_text_by_kms(os.getenv('SlackUrl'))
    attachments_json = [
        {
            "color": color,
            "title": title,
            "fields": [
                {
                    "title": "command_id",
                    "value": command_id,
                    "short": True
                },
                {
                    "title": "ステータス",
                    "value": status,
                    "short": True
                },
                {
                    "title": "インスタンスID",
                    "value": instance_id,
                    "short": True
                },
                {
                    "title": "Nameタグ",
                    "value": instance_name,
                    "short": True
                },
                {
                    "title": "開始時刻",
                    "value": requested_date_time,
                    "short": True
                },
                {
                    "title": "終了時刻",
                    "value": finish_time,
                    "short": True
                }
            ]
        }
    ]
    slack_message = {
        'attachments': attachments_json
    }
    req = Request(slack_url, json.dumps(slack_message).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted")
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)


def lambda_handler(event, context):
    command_id = event['detail']['command-id']
    instance_id = event['detail']['instance-id']
    document_name = event['detail']['document-name']
    status = event['detail']['status']
    finish_time = event['time']
    requested_date_time = event['detail']['requested-date-time']

    instance = ec2.Instance(instance_id)
    name_tag = [tag['Value'] for tag in instance.tags if tag['Key'] == 'Name']
    instance_name = name_tag[0] if len(name_tag) else ''

    if (status == 'Success'):
        color = 'good'
    else:
        color = 'warning'
    notify_slack(
        document_name + '結果',
        command_id,
        instance_id,
        instance_name,
        status,
        requested_date_time,
        finish_time,
        color
    )
