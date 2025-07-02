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
dotenv python src/producer_azsb_library.py --update-record-type dataset --update-type delete

dotenv python src/producer_azsb_library.py --update-record-type reporting_org --update-type update
```

You can also specify a given UUID to use for the main data item which is helpful
if you want to test against known data:

```bash
dotenv python src/producer_azsb_library.py --update-record-type reporting_org \
                                           --update-type update \
                                           --uuid-to-use bd87b5e6-1704-4dcc-9979-efd54358bb2b
```

To receive some messages:

```bash
dotenv python src/consumer_azsb_library.py --num-messages-to-receive 5
```

## Development on the samples

If you change the dev dependencies, recompile the development dependencies:

```bash
pip-compile --upgrade --extra dev -o requirements-dev.txt pyproject.toml
```

If you change the code, install the dev dependencies so `isort`, `black`, etc
can be run:

```bash
pip install -r requirements-dev.txt
```

Running the linters:

```bash
isort .

black src

mypy

flake8 src
```

