#!/bin/bash
# delete_uploads.sh

# Delete uploads
dir="/home/scott/WordCloud_Web/uploads"

# Delete All
rm -rf "${dir:?}"/*
