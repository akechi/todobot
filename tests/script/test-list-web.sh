#!/bin/sh

curl -X POST -d "{\"events\":[{\"message\":{\"text\":\"#todo list\",\"speaker_id\":\"bgnori\",\"room\":\"bgnori\"}}]}" http://todo.tonic-water.com/lingrbot 
