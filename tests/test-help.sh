#!/bin/sh

curl -X POST -d "{\"events\":[{\"message\":{\"text\":\"#todo help\",\"speaker_id\":\"raa0121\",\"room\":\"computer_science\"}}]}" http://127.0.0.1:5000/lingrbot 
