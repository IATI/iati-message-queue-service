import argparse
import asyncio
import os
from datetime import datetime

from azure.servicebus.aio import ServiceBusClient


async def serviceloop(context: dict):
    while True:
        try:
            print("Sample consumer - service loop - mark - {}".format(datetime.now().isoformat()))
            await receive_some_messages(context)
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            raise


async def receive_some_messages(context: dict):

    try:
        async with ServiceBusClient.from_connection_string(
            conn_str=context["connection_string"], logging_enable=True
        ) as servicebus_client:
            async with servicebus_client:
                receiver = servicebus_client.get_subscription_receiver(
                    topic_name=context["topic_name"],
                    subscription_name=context["subscription_name"],
                    max_wait_time=2,
                    mode=context["mode"],
                )
                async with receiver:
                    if context["mode"] == "PEEK_LOCK":
                        received_msgs = await receiver.peek_messages(
                            max_message_count=context["num_messages_to_receive"]
                        )
                        for msg in received_msgs:
                            print("Message peeked:")
                            print(str(msg))
                            # await receiver.abandon_message(msg)
                    else:
                        received_msgs = await receiver.receive_messages(
                            max_wait_time=2, max_message_count=context["num_messages_to_receive"]
                        )
                        for msg in received_msgs:
                            print("Message received: ")
                            print(str(msg))
                            await receiver.complete_message(msg)

    except asyncio.CancelledError:
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IATI Message Queue Sample App")
    parser.add_argument(
        "--num-messages-to-receive",
        type=int,
        required=True,
        help="How many messages to receive (only really relevant if not in service loop)",
    )
    parser.add_argument(
        "--run-as-service-loop",
        action="store_true",
        required=False,
        help="Run forever, waiting and receiving messages",
    )
    parser.add_argument(
        "--mode",
        choices=["peek", "receive"],
        required=False,
        help="Mode = peek, view messages; receive = receive and delete",
    )

    args = parser.parse_args()

    context = {
        "connection_string": os.getenv("AZ_SERVICE_BUS_CONNECTION_STRING"),
        "topic_name": os.getenv("AZ_SERVICE_BUS_TOPIC_NAME"),
        "subscription_name": os.getenv("AZ_SERVICE_BUS_SUBSCRIPTION_NAME"),
        "num_messages_to_receive": args.num_messages_to_receive,
        "mode": "PEEK_LOCK" if args.mode == "peek" else "RECEIVE_AND_DELETE",
    }

    if args.run_as_service_loop:
        try:
            asyncio.run(serviceloop(context))
        except KeyboardInterrupt:
            print("\nUser pressed Ctrl-C. Stopping receiving messages and exiting")
    else:
        try:
            asyncio.run(receive_some_messages(context))
        except KeyboardInterrupt:
            print("\nUser pressed Ctrl-C. Exiting")
