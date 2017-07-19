#!/bin/bash

shared="/home/scom/Documents/RoboCupSimulation2D_teams_ranking_by_BayesStats/"

docker run --rm --net=host -p 127.0.0.1:6001:6001 -v $shared:/robocup/shared/ -it bayesranking:latest /bin/bash
