#!/bin/bash

rsync -avzuiP ./* localpi:~/SoccerRobot \
    --exclude ControlServer/.next \
    --exclude *__pycache__

rsync -avzuiP localpi:~/SoccerRobot/* . \
    --exclude *__pycache__ \
    --exclude ControlServer/out \