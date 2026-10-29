#!/usr/bin/env bash
# Removes the Kind cluster (and all its data, including the Postgres volume).
set -euo pipefail

kind delete cluster --name taskapp
