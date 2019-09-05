#!/bin/bash

rsync -avzuiP ./* localpi:~/SoccerRobot \
    --delete \
    --exclude data \
    --exclude ControlServer/out \
    --exclude *__pycache__

rsync -avzuiP localpi:~/SoccerRobot/* . \
    --ignore-existing \
    --exclude data \
    --exclude *__pycache__