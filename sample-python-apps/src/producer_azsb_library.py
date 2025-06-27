import os
import asyncio
import argparse
import json
import uuid
from datetime import datetime
from random import randint
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage


def get_sample_reporting_org_short_name():
    names = ["aidplan", "aidsupport", "allaid", "ukaid", "aidforall", "allaid"]
    return names[randint(0, len(names) - 1)]


def get_sample_dataset_short_name(reporting_org: str):
    names = ["activities", "act-01", "act2", "org", "organisation", "data", "new-data"]
    return "{}-{}".format(reporting_org, names[randint(0, len(names) - 1)])


def generate_sample_reporting_org_update_message():
    reporting_org_short_name = get_sample_reporting_org_short_name()
    reporting_org_name = reporting_org_short_name.capitalize() + " Agency"
    dataset = get_sample_dataset_short_name(reporting_org_short_name)
    return { "message_type": "REPORTING_ORG_UPDATED",
             "reporting_org": { 
                 "id": str(uuid.uuid4()),
                 "short_name": reporting_org_short_name,
                 "human_readable_name": reporting_org_name,
                 "hq_country": "United Kingdom",
                 "region": "Europe",
                 "iati_organisation_identifier": "GB-AGY-" + str(randint(100, 900)),
                 "iati_organisation_type": "National NGO",
                 "data_portal_url": "https://www.example.org/data-portal/",
                 "exclusions_policy_url": "https://www.example.org/exclusions.html",
                 "reporting_source_type": "primary-source" if randint(0, 10) > 5 else "secondary-source",
                 "default_licence_id": "cc-by",
                 "contact_email": "sample@example.org",
                 "address": "123 Main Road, Easytown, Exampleshire",
                 "phone": "01234 567 890",
                 "first_publication_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "number_of_published_datasets": randint(0, 10),
             }}


def generate_sample_dataset_update_message():
    reporting_org = get_sample_reporting_org_short_name()
    dataset = get_sample_dataset_short_name(reporting_org)

    return { "message_type": "DATASET_UPDATED",
             "reporting_org": { 
                 "id": str(uuid.uuid4()),
                 "short_name": dataset,
                 "source_type": "primary-source" if randint(0, 10) > 5 else "secondary-source",
                 "url": "https://www.example.org/{}.xml".format(dataset),
                 "last_url_update_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "last_metadata_update_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "reporting_org_id": str(uuid.uuid4()),
                 "reporting_org_short_name": reporting_org,
             }}


def generate_example_payload(update_message_type):
    if update_message_type == "dataset":
        payload = generate_sample_dataset_update_message()
    else:
        payload = generate_sample_reporting_org_update_message()
    return json.dumps(payload, indent=2)


async def send_single_message(update_message_type: str, topic_sender):
    sample_message = generate_example_payload(update_message_type)
    message = ServiceBusMessage(sample_message)
    await topic_sender.send_messages(message)
    print("Generated and sent the following sample {} update message:".format(update_message_type))
    print(sample_message)


async def main(args: argparse.Namespace):
    conn_str = os.getenv("AZ_SERVICE_BUS_CONNECTION_STRING")
    topic_name = os.getenv("AZ_SERVICE_BUS_TOPIC_NAME")
    
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=conn_str, logging_enable=True)
    topic_sender = servicebus_client.get_topic_sender(topic_name=topic_name)
    await send_single_message(args.update_message_type, topic_sender)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IATI Message Queue Sample App")
    parser.add_argument(
        "--update-message-type",
        choices=["dataset", "reporting_org"],
        required=True,
        help="Which type of update message to send",
    )
    asyncio.run(main(parser.parse_args()))
