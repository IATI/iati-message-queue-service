# Sample Apps

## Setup

Setup a Python virtual environment, then:

```bash
pip install pip-tools

pip-compile pyproject.toml

pip install -r requirements.txt
```

Populate `AZ_SERVICE_BUS_CONNECTION_STRING` in the `.env` file in
`sample-python-apps` with a valid connection string. The connection strings can
be found in the Azure Portal under the Service Bus Namespace resource. If you
use the one that is created for the Data Getter, then it will have permissions
to send and receive, so you can use the same key for both sample apps.


## Usage

(If you don't want to use `dotenv`, source `.env` into your current terminal).

To send a message using a Python client that uses the Azure Service Bus library:

```bash
dotenv python src/producer_azsb_library.py --update-message-type dataset

dotenv python src/producer_azsb_library.py --update-message-type reporting_org
```

To receive some messages:

```bash
dotenv python src/consumer_azsb_library.py --num-messages-to-receive 5
```

