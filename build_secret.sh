#!/bin/sh

host="$1"
user="$2"
password="$3"

if [[ ! -e secret.json ]]; then
	touch secret.json
	echo "{\"host\":\"$host\",\"user\":\"$user\",\"password\":\"$password\",\"database\":\"TheSocialNetwork\"}" >> secret.json
fi
