#!/bin/bash

echo curl boldhorse.servebeer.com:901/recognize -F "image=@./$1"
# curl boldhorse.servebeer.com:901/recognize -F "image=@./$1"


curl localhost:8080/recognize -F "image=@./$1"