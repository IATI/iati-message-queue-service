#!/usr/bin/env bash


asyncapi generate fromTemplate specification/iati-mq-suitecrm.yaml @asyncapi/html-template@3.0.0 -o docs/specification-mq-suitecrm --use-new-generator --force-write
asyncapi generate fromTemplate specification/iati-mq-clients.yaml @asyncapi/html-template@3.0.0 -o docs/specification-mq-clients --use-new-generator --force-write
