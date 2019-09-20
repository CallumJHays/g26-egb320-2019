#!/bin/bash

rsync -avzuiP ./* localpi:~/SoccerRobot \
    --exclude data \
    --exclude ControlServer/out \
    --exclude ControlServer/.next \
    --exclude *__pycache__

rsync -avzuiP localpi:~/SoccerRobot/* . \
    --exclude data \
    --exclude *__pycache__