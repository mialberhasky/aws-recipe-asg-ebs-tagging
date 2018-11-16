See blog entry about this repository at: [https://www.michaelalberhasky.com/coding/2018/11/03/aws-asg-tagging.html](https://www.michaelalberhasky.com/coding/2018/11/03/aws-asg-tagging.html)

### Why?
This module contains two Python files for managing EBS volumes created when launching EC2 instances inside of an auto-scaling 
group. There is no native mechanism (currently) to add tags to a volume when it launches via an auto-scaling event. We have 
to do it through Lambda.

### How to setup/deploy
Since we need some dependencies, we need to import them. This assumes you have `virtualenv` installed. At this time, this
function uses Python 2.7. First so these this from this directory:
  
    virtualenv -p /usr/bin/python2.7 env
    
    source env/bin/activate
    
    pip install -r requirements.txt
    
After you have the dependencies installed, you can run the build script

    ./build.sh
    
This copies our Python files in the `src` directory to the `dist` directory as well as all the dependencies we imported into 
the virtualenv. The result is a zip file with everything we need. 

This zip file can be uploaded to a S3 bucket which contains code artifacts. Then the CloudFormation stack can be updated to point to this new package.