#!/bin/bash

NAME="irctc_ocr"

if [[ $1 == "--build" || $1 == "-b" ]];then
    docker build . -t $NAME

elif [[ $1 == "--run" || $1 == "-r" ]];then
    docker run --rm -it \
        -v $(pwd):/app \
        -p 8210:5000 \
        --name $NAME \
        --hostname $NAME \
        $NAME bash

elif [[ $1 == "--attach" || $1 == "-a" ]];then
    docker exec -it $NAME bash
fi