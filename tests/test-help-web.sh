#!/bin/sh

curl -X POST -d "{\"events\":[{\"message\":{\"text\":\"#todo help\",\"speaker_id\":\"bgnori\",\"room\":\"bgnori\"}}]}" http://todo.tonic-water.com/lingrbot 
