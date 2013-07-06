#!/bin/sh

curl -X POST -d "{\"events\":[{\"message\":{\"text\":\"#todo add test1\",\"speaker_id\":\"bgnori\",\"room\":\"bgnori\"}}]}" http://127.0.0.1:5000/lingrbot 
