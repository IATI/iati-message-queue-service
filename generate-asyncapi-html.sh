#!/usr/bin/bash

set -o errexit   # abort on nonzero exitstatus
set -o nounset   # abort on unbound variable
set -o pipefail  # don't hide errors within pipes

asyncapi generate fromTemplate specification/iati-registry.yaml @asyncapi/html-template@3.0.0 -o docs/spec-iati-registry --use-new-generator --force-write

asyncapi generate fromTemplate specification/iati-dashboard.yaml @asyncapi/html-template@3.0.0 -o docs/spec-iati-dashboard --use-new-generator --force-write

asyncapi generate fromTemplate specification/iati-bulk-data-service.yaml @asyncapi/html-template@3.0.0 -o docs/spec-iati-bulk-data-service --use-new-generator --force-write

asyncapi generate fromTemplate specification/iati-data-downloader.yaml @asyncapi/html-template@3.0.0 -o docs/spec-iati-data-downloader --use-new-generator --force-write
