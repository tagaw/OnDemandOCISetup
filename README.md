# OnDemandOCISetup
A template to automatically start up a Minecraft server on an OCI compute instance. 


## Instructions
1. Set up an OCI compute instance
2. Download the repo in to any directory you would like
3. Install all python requirements found in requirements.txt
4. Set up appropriate ENV_VARS in `.env`
5. __INSIDE__ the downloaded directory, setup a MC server to start with a runserver.sh script (default for many forge servers) 
6. Setup a crontab job (sudo optional) by using the crontabcommand.txt file for reference