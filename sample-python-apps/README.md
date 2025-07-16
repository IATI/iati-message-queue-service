# Sample Apps

## Setup

Setup a Python virtual environment, then:

```bash
pip install -r requirements.txt
```

Populate `AZ_SERVICE_BUS_CONNECTION_STRING` in the `.env` file in
`sample-python-apps` with a valid connection string. The connection strings can
be found in the Azure Portal under the Service Bus Namespace resource. If you
use the one that is created for the Data Getter, then it will have permissions
to send and receive, so you can use the same key for both sample apps.


## Usage

Copy `.env-example` to `.env` and fill in the details.

Using `dotenv` means you can have multiple `.env-N` files set and then switch
between them with `dotenv -e ENV_FILE` but if you don't want to use `dotenv` you
can just source the `.env` file into your terminal.

To send a message using a Python client that uses the Azure Service Bus library:

```bash
dotenv python src/producer_azsb_library.py --update-record-type dataset --update-type deleted

dotenv python src/producer_azsb_library.py --update-record-type reporting_org --update-type updated
```

`--update-record-type` can be either `dataset` or `reporting_org`

`--update-type` can be `created`, `updated`, or `deleted`.

You can also specify a given UUID to use for the dataset and/or reporting_org
which is helpful if you want to test against known data:

```bash
dotenv python src/producer_azsb_library.py --update-record-type dataset \
                                           --update-type updated \
                                           --dataset-uuid bd87b5e6-1704-4dcc-9979-efd54358bb2b \
                                           --reporting-org-uuid 7e9835be-6250-11f0-b2e6-37356d2fe5ee
```

You can also specify the dataset short name and reporting org short name.

To receive some messages (removing them from the queue):

```bash
dotenv python src/consumer_azsb_library.py --num-messages-to-receive 5
```

To peek at some messages without removing them from the queue:

```bash
dotenv python src/consumer_azsb_library.py --num-messages-to-receive 5 --mode peek
```

To run in a loop receiving messages indefinitely (until you press Ctrl-C):

```bash
dotenv python src/consumer_azsb_library.py --num-messages-to-receive 5 --mode peek --run-as-service-loop
```

## Development on the samples

If you change the dev dependencies, recompile the development dependencies:

```bash
pip install pip-tools

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

