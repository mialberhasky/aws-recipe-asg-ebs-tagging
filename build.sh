#!/usr/bin/env bash

cp -rf src dist
cp -rf env/lib/python2.7/site-packages/* dist
cd dist
zip -r9 ../ebs-asg-manage.zip .
