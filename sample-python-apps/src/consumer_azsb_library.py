import os
import asyncio
import argparse
from random import randint
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage


async def main(args: argparse.Namespace):
    conn_str = os.getenv("AZ_SERVICE_BUS_CONNECTION_STRING")
    topic_name = os.getenv("AZ_SERVICE_BUS_TOPIC_NAME")
    subscription_name = os.getenv("AZ_SERVICE_BUS_SUBSCRIPTION_NAME")

    async with ServiceBusClient.from_connection_string(conn_str=conn_str, logging_enable=True) as servicebus_client:
        async with servicebus_client:
            receiver = servicebus_client.get_subscription_receiver(topic_name=topic_name, subscription_name=subscription_name, max_wait_time=1)
            async with receiver:
                received_msgs = await receiver.receive_messages(max_wait_time=1, max_message_count=args.num_messages_to_receive)
                for msg in received_msgs:
                    print("Message received: ")
                    print (str(msg))
                    await receiver.complete_message(msg)  # complete message, so removed from queue/topic



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IATI Message Queue Sample App")
    parser.add_argument(
        "--num-messages-to-receive",
        type=int,
        required=True,
        help="How many messages to receive",
    )
    asyncio.run(main(parser.parse_args()))
