#!/bin/sh
cd "$(dirname "$0")"
rsync -avz --delete public/ backl:/var/www/howto.philippkeller.com/
