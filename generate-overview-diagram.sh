#!/usr/bin/bash

# It is not intended to run this locally and commit the changes. This script
# is run from the GitHub Workflow `generate-overview-diagram.yaml` on pushes
# to develop

set -o errexit   # abort on nonzero exitstatus
set -o nounset   # abort on unbound variable
set -o pipefail  # don't hide errors within pipes

cat docs/iati-message-queue-service-and-apps-overview.puml | docker run -i ghcr.io/plantuml/plantuml -pipe > docs/iati-message-queue-service-and-apps-overview.png
