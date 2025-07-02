import argparse
import asyncio
import os

from azure.servicebus.aio import ServiceBusClient


async def serviceloop(context: dict):
    while True:
        await receive_some_messages(context)
        await asyncio.sleep(2)


async def receive_some_messages(context: dict):
    async with ServiceBusClient.from_connection_string(
        conn_str=context["connection_string"], logging_enable=True
    ) as servicebus_client:
        async with servicebus_client:
            receiver = servicebus_client.get_subscription_receiver(
                topic_name=context["topic_name"], subscription_name=context["subscription_name"], max_wait_time=1
            )
            async with receiver:
                received_msgs = await receiver.receive_messages(
                    max_wait_time=1800, max_message_count=args.num_messages_to_receive
                )
                for msg in received_msgs:
                    print("Message received: ")
                    print(str(msg))
                    await receiver.complete_message(msg)  # complete message, so removed from queue/topic


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

    args = parser.parse_args()

    context = {
        "connection_string": os.getenv("AZ_SERVICE_BUS_CONNECTION_STRING"),
        "topic_name": os.getenv("AZ_SERVICE_BUS_TOPIC_NAME"),
        "subscription_name": os.getenv("AZ_SERVICE_BUS_SUBSCRIPTION_NAME"),
        "num_messages_to_receive": args.num_messages_to_receive,
    }

    if args.run_as_service_loop:
        asyncio.run(serviceloop(context))
    else:
        asyncio.run(receive_some_messages(context))
