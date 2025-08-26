import argparse
import asyncio
import copy
import json
import os
import uuid
from datetime import datetime, timedelta
from functools import reduce
from random import randint
from typing import Any  # noqa: F401

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
        "message_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        record_type_to_delete: {
            "id": uuid_to_use if uuid_to_use is not None else str(uuid.uuid4()),
        },
    }


def generate_sample_reporting_org_message(update_type: str, reporting_org_fields: dict):
    reporting_org_short_name_calc = reporting_org_fields.get("short_name", get_sample_reporting_org_short_name())
    reporting_org_name = reporting_org_short_name_calc.replace("-", " ").title()

    return {
        "message_type": f"{update_type.upper()}",
        "message_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "reporting_org": {
            "created_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "data_portal_url": "https://www.example.org/data-portal/",
            "default_licence_id": "cc-by",
            "description": fake.text(),
            "exclusions_policy_url": "https://www.example.org/exclusions.html",
            "first_publication_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "hq_country": "GB",
            "human_readable_name": reporting_org_name,
            "organisation_identifier": "GB-AGY-" + str(randint(100, 900)),
            "organisation_type": "73",
            "id": reporting_org_fields.get("id", str(uuid.uuid4())),
            "region": "89",
            "reporting_source_type": "primary-source" if randint(0, 10) > 5 else "secondary-source",
            "short_name": reporting_org_short_name_calc,
            "website": "https://www.example.org",
        },
    }


def generate_sample_dataset_message(update_type: str, dataset_fields: dict, reporting_org_fields: dict) -> dict:
    reporting_org = get_sample_reporting_org_short_name()
    dataset_sample_short_name = get_sample_dataset_short_name(reporting_org)

    return {
        "message_type": f"{update_type.upper()}",
        "message_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "dataset": {
            "id": dataset_fields.get("id", str(uuid.uuid4())),
            "short_name": dataset_fields.get("id", dataset_sample_short_name),
            "source_type": "primary-source" if randint(0, 10) > 5 else "secondary-source",
            "licence_id": get_sample_dataset_licence_id(),
            "url": "https://www.example.org/{}.xml".format(dataset_sample_short_name),
            "last_url_update_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "last_metadata_update_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "reporting_org_id": reporting_org_fields.get("id", str(uuid.uuid4())),
            "reporting_org_short_name": reporting_org,
        },
    }


def generate_download_request_message(dataset_fields: dict, reporting_org_fields: dict) -> dict:
    reporting_org = get_sample_reporting_org_short_name()
    dataset_sample_short_name = get_sample_dataset_short_name(reporting_org)
    return {
        "message_type": "DATASET_DOWNLOAD_REQUEST",
        "message_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "dataset": {
            "id": dataset_fields.get("id", str(uuid.uuid4())),
            "short_name": dataset_fields.get("short_name", dataset_sample_short_name),
            "source_type": "primary-source" if randint(0, 10) > 5 else "secondary-source",
            "licence_id": get_sample_dataset_licence_id(),
            "url": dataset_fields.get("url", "https://www.example.org/{}.xml".format(dataset_sample_short_name)),
            "last_url_update_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "last_metadata_update_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "reporting_org_id": reporting_org_fields.get("id", str(uuid.uuid4())),
            "reporting_org_short_name": reporting_org_fields.get("short_name", reporting_org),
        },
        "dataset_hash_details": {
            "hash": dataset_fields.get("hash", "5c5d7e150145f34975485e6a4b862d5f238f7f84"),
            "hash_excluding_generated_timestamp": dataset_fields.get(
                "hash", "5c5d7e150145f34975485e6a4b862d5f238f7f84"
            ),
        },
    }


def generate_dataset_check_message(dataset_fields: dict, reporting_org_fields: dict, content_changed: bool) -> dict:
    reporting_org_sample_name = get_sample_reporting_org_short_name()

    dataset_sample_name = get_sample_dataset_short_name(reporting_org_sample_name)

    source_url = dataset_fields.get("source_url", "https://www.example.org/{}.xml".format(dataset_sample_name))

    result = {
        "message_type": "DATASET_CHECK_RESULT",
        "message_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "dataset_check_result_current": {
            "id": dataset_fields.get("id", str(uuid.uuid4())),
            "short_name": dataset_fields.get("short_name", dataset_sample_name),
            "reporting_org_id": reporting_org_fields.get("id", str(uuid.uuid4())),
            "reporting_org_short_name": reporting_org_fields.get("short_name", reporting_org_sample_name),
            "licence_id": get_sample_dataset_licence_id(),
            "source_url": source_url,
            "last_update_check": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "last_known_good_dataset": {
                "cached_dataset_xml_url": "test.org/download.xml",
                "cached_dataset_xml_etag": "KXDMHBNCLJWWUV",
                "cached_dataset_zip_url": "test.org/download.zip",
                "cached_dataset_zip_etag": "CLJWWUVKXDMHBN",
                "content_length": 725211,
                "downloaded": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                "hash": "e1196c7c1fc763f45c5114ed50957981abd21720",
                "hash_excluding_generated_timestamp": "4ed50957981abd21720e1196c7c1fc763f45c511",
                "initial_contents": "<iati-activities><iati-activity>qweqwe",
                "server_header_etag": "KXDMHWWUVBNCLJ",
                "server_header_last_modified": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                "source_url": source_url,
                "verified_on_server": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            },
            "most_recent_head_attempt": {
                "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                "error_details": {},
                "error_occurred": False,
                "http_status": 200,
            },
            "most_recent_get_attempt": {
                "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                "error_details": {},
                "error_occurred": False,
                "http_status": 200,
            },
        },
    }  # type: dict[str, Any]

    previous_result = copy.deepcopy(result["dataset_check_result_current"])

    # update the date fields
    previous_datetime = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    previous_result["last_update_check"] = previous_datetime
    previous_result["most_recent_head_attempt"]["datetime"] = previous_datetime
    previous_result["most_recent_get_attempt"]["datetime"] = previous_datetime
    previous_result["last_known_good_dataset"]["downloaded"] = previous_datetime
    previous_result["last_known_good_dataset"]["server_header_last_modified"] = previous_datetime
    previous_result["last_known_good_dataset"]["verified_on_server"] = previous_datetime

    # update the fields that would be changed by a dataset content change
    if content_changed:
        previous_result["last_known_good_dataset"]["hash"] = "c5114ed50957981abd21720e1196c7c1fc763f45"
        previous_result["last_known_good_dataset"][
            "hash_excluding_generated_timestamp"
        ] = "45c5114ed50957981abd21720e1196c7c1fc763f"

    result["dataset_check_result_previous"] = previous_result

    return result


def generate_example_payload(args: argparse.Namespace) -> dict:
    dataset_fields = {f"{k}": v for k, v in map(lambda x: x.split("="), args.dataset_fields)}
    reporting_org_fields = {f"{k}": v for k, v in map(lambda x: x.split("="), args.reporting_org_fields)}

    if args.message_type == "dataset_check_result":
        payload = generate_dataset_check_message(
            dataset_fields, reporting_org_fields, args.dataset_check_result_content_changed
        )
    elif args.message_type == "dataset_download_request":
        payload = generate_download_request_message(dataset_fields, reporting_org_fields)
    elif args.message_type.endswith("deleted"):
        record_type = args.message_type.replace("_deleted", "")
        primary_uuid = (
            dataset_fields.get("id", None) if record_type == "dataset" else reporting_org_fields.get("id", None)
        )
        payload = generate_sample_delete_message(record_type, primary_uuid)
    else:
        record_type = (
            args.message_type.replace("_updated", "")
            if args.message_type.endswith("_updated")
            else args.message_type.replace("_created", "")
        )
        if record_type == "dataset":
            payload = generate_sample_dataset_message(args.message_type, dataset_fields, reporting_org_fields)
        else:
            payload = generate_sample_reporting_org_message(args.message_type, reporting_org_fields)
    return payload


async def send_single_message(sender: ServiceBusSender, args: argparse.Namespace):

    msg_payload = generate_example_payload(args)

    msg_payload_as_str = json.dumps(msg_payload, indent=2)

    message = ServiceBusMessage(
        body=msg_payload_as_str, application_properties={"message_type": msg_payload["message_type"]}
    )

    await sender.send_messages(message)

    output = {
        "info": "Generated and sent a sample {} message".format(args.message_type),
        "message_payload": msg_payload,
    }

    print(json.dumps(output, indent=2))


async def main(args: argparse.Namespace):
    conn_str = os.getenv("AZ_SERVICE_BUS_CONNECTION_STRING", "")
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=conn_str, logging_enable=True)

    sender_type, channel_name = os.getenv(args.message_type.upper() + "_SENDER", ",").split(",")

    if sender_type == "queue":
        sender = servicebus_client.get_queue_sender(queue_name=channel_name)
    else:
        sender = servicebus_client.get_topic_sender(topic_name=channel_name)

    await send_single_message(sender, args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IATI MQ Sample App - Producer")
    parser.add_argument(
        "--message-type",
        choices=[
            "dataset_created",
            "dataset_updated",
            "dataset_deleted",
            "dataset_download_request",
            "dataset_check_result",
            "reporting_org_created",
            "reporting_org_updated",
            "reporting_org_deleted",
        ],
        required=True,
        help="Which type of message to send",
    )
    parser.add_argument(
        "--dataset-check-result-content-changed",
        action="store_true",
        required=False,
        default=False,
        help="Whether to modify the hash on a DATASET_CHECK_RESULT message",
    )
    parser.add_argument(
        "--dataset-fields",
        type=str,
        required=False,
        default=[],
        nargs="*",
        help="Fields to use for the dataset record, in format field=value",
    )
    parser.add_argument(
        "--reporting-org-fields",
        type=str,
        required=False,
        default=[],
        nargs="*",
        help="Fields to use for the reporting org record, in format field=value",
    )
    asyncio.run(main(parser.parse_args()))
