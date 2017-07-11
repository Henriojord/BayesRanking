#!/bin/bash

shared="/home/scom/Documents/RoboCupSimulation2D_teams_ranking_by_BayesStats/docker_share/"

docker run --rm --net=host -v $shared:/robocup/shared/ -it bayesranking:latest /bin/bash
