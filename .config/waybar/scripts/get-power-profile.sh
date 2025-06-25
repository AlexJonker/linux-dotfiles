#!/bin/bash

# Get power profile
POWER_PROFILE=$(powerprofilesctl get)

# Format the tooltip message
echo "$POWER_PROFILE"
