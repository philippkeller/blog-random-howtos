#!/bin/sh
cd "$(dirname "$0")"
aws s3 sync public s3://howto.philippkeller.com/ --profile private
