import argparse
import asyncio
import json
import os
import uuid
from datetime import datetime
from functools import reduce
from random import randint

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient, ServiceBusSender
from faker import Faker

fake = Faker("en_GB")


def get_sample_name(n):
    return reduce(lambda x, y: "-".join([x, y]), map(lambda x: fake.word(), range(n)))


def get_sample_reporting_org_short_name():
    return "org-" + get_sample_name(1)


def get_sample_dataset_short_name(reporting_org: str):
    return "{}-{}".format(reporting_org, get_sample_name(2))


def get_sample_dataset_licence_id() -> str:
    licences = ["cc-by", "gfdl", "odc-by", "uk-ogl"]
    return licences[randint(0, len(licences) - 1)]


def generate_sample_delete_message(record_type_to_delete: str, uuid_to_use: str | None = None) -> dict:

    return {
        "message_type": "{}_DELETED".format(record_type_to_delete.upper()),
        "message_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        record_type_to_delete: {
            "id": uuid_to_use if uuid_to_use is not None else str(uuid.uuid4()),
        },
    }


def generate_sample_reporting_org_message(
    update_type: str, reporting_org_uuid: str | None = None, reporting_org_short_name: str | None = None
):
    reporting_org_short_name_calc = (
        reporting_org_short_name if reporting_org_short_name is not None else get_sample_reporting_org_short_name()
    )
    reporting_org_name = reporting_org_short_name_calc.replace("-", " ").title()

    return {
        "message_type": f"REPORTING_ORG_{update_type.upper()}",
        "message_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reporting_org": {
            "id": reporting_org_uuid if reporting_org_uuid is not None else str(uuid.uuid4()),
            "short_name": reporting_org_short_name_calc,
            "human_readable_name": reporting_org_name,
            "hq_country": "United Kingdom",
            "region": "Europe",
            "iati_organisation_identifier": "GB-AGY-" + str(randint(100, 900)),
            "iati_organisation_type": "National NGO",
            "data_portal_url": "https://www.example.org/data-portal/",
            "exclusions_policy_url": "https://www.example.org/exclusions.html",
            "reporting_source_type": "primary-source" if randint(0, 10) > 5 else "secondary-source",
            "default_licence_id": "cc-by",
            "contact_email": fake.email(),
            "address": fake.address().replace("\n", ", "),
            "phone": fake.phone_number(),
            "first_publication_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "number_of_published_datasets": randint(0, 50),
        },
    }


def generate_sample_dataset_message(
    update_type: str,
    dataset_uuid: str | None = None,
    dataset_short_name: str | None = None,
    reporting_org_uuid: str | None = None,
):
    reporting_org = get_sample_reporting_org_short_name()
    dataset_sample_short_name = get_sample_dataset_short_name(reporting_org)

    return {
        "message_type": f"DATASET_{update_type.upper()}",
        "message_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dataset": {
            "id": dataset_uuid if dataset_uuid is not None else str(uuid.uuid4()),
            "short_name": dataset_short_name if dataset_short_name is not None else dataset_sample_short_name,
            "source_type": "primary-source" if randint(0, 10) > 5 else "secondary-source",
            "licence_id": get_sample_dataset_licence_id(),
            "url": "https://www.example.org/{}.xml".format(dataset_sample_short_name),
            "last_url_update_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_metadata_update_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "reporting_org_id": reporting_org_uuid if reporting_org_uuid is not None else str(uuid.uuid4()),
            "reporting_org_short_name": reporting_org,
        },
    }


def generate_example_payload(
    update_type: str,
    update_record_type: str,
    dataset_uuid: str,
    dataset_short_name: str,
    reporting_org_uuid: str,
    reporting_org_short_name: str,
) -> dict:
    if update_type == "deleted":
        primary_uuid = dataset_uuid if update_record_type == "dataset" else reporting_org_uuid
        payload = generate_sample_delete_message(update_record_type, primary_uuid)
    else:
        if update_record_type == "dataset":
            payload = generate_sample_dataset_message(
                update_type, dataset_uuid, dataset_short_name, reporting_org_uuid
            )
        else:
            payload = generate_sample_reporting_org_message(update_type, reporting_org_uuid, reporting_org_short_name)
    return payload


async def send_single_message(
    update_type: str,
    update_record_type: str,
    dataset_uuid: str,
    dataset_short_name: str,
    reporting_org_uuid: str,
    reporting_org_short_name: str,
    topic_sender: ServiceBusSender,
):
    msg_payload = generate_example_payload(
        update_type, update_record_type, dataset_uuid, dataset_short_name, reporting_org_uuid, reporting_org_short_name
    )
    msg_payload_as_str = json.dumps(msg_payload, indent=2)
    message = ServiceBusMessage(
        body=msg_payload_as_str, application_properties={"message_type": msg_payload["message_type"]}
    )
    await topic_sender.send_messages(message)
    output = {
        "info": "Generated and sent a sample {} {} message".format(update_type, update_record_type),
        "message_payload": msg_payload,
    }
    print(json.dumps(output, indent=2))


async def main(args: argparse.Namespace):
    conn_str = os.getenv("AZ_SERVICE_BUS_CONNECTION_STRING", "")
    topic_name = os.getenv("AZ_SERVICE_BUS_TOPIC_NAME", "")

    servicebus_client = ServiceBusClient.from_connection_string(conn_str=conn_str, logging_enable=True)
    topic_sender = servicebus_client.get_topic_sender(topic_name=topic_name)
    await send_single_message(
        args.update_type,
        args.update_record_type,
        args.dataset_uuid,
        args.dataset_short_name,
        args.reporting_org_uuid,
        args.reporting_org_short_name,
        topic_sender,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IATI Message Queue Sample App")
    parser.add_argument(
        "--update-type",
        choices=["created", "updated", "deleted"],
        required=True,
        help="Which type of update message to send",
    )
    parser.add_argument(
        "--update-record-type",
        choices=["dataset", "reporting_org"],
        required=True,
        help="Which type of data record to create a message for",
    )
    parser.add_argument(
        "--dataset-uuid",
        type=str,
        required=False,
        help="Use the specified UUID in for the dataset id",
    )
    parser.add_argument(
        "--dataset-short-name",
        type=str,
        required=False,
        help="Use the specified short-name for the dataset",
    )
    parser.add_argument(
        "--reporting-org-uuid",
        type=str,
        required=False,
        help="Use the specified UUID in for the reporting org id",
    )
    parser.add_argument(
        "--reporting-org-short-name",
        type=str,
        required=False,
        help="Use the specified short-name for the reporting org",
    )
    asyncio.run(main(parser.parse_args()))
