#!/bin/bash

set -e

MEDIA_DIR="./ssn/media"
for sub in previews comprobantes; do
  mkdir -p "$MEDIA_DIR/$sub"
  chmod 775 "$MEDIA_DIR/$sub"
  chown $(id -u):$(id -g) "$MEDIA_DIR/$sub"
done
