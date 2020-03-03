set -e 
set -u

CONTAINER_NAME=betfairstreamer
TAG_NAME=$(git rev-parse HEAD)

# If container already exist, start if it is not already running
if [ "$(docker ps -a | grep $CONTAINER_NAME:$TAG_NAME)" ]
then
    echo "Container already exists, only rebuilds on new commits!"
	docker start $CONTAINER_NAME
    exit 0
fi

# Build a new image if it does not exist.
if [ ! "$(docker images -a | grep $CONTAINER_NAME:$TAG_NAME)" ]
then
	docker build -t $CONTAINER_NAME:$TAG_NAME .
fi

# File containing your credentials to betfair.
# This is just an example, you should probably store your credentials somewhere else
# and inject them here.
source credentials.env

# USERNAME: Betfair login user
# PASSWORD: Betfair login password
# APP_KEY: Application key
# CERT_PATH: Path where certs are is mounted in container.


docker run \
	   -p 5556:5556 \
	   -p 5557:5557 \
	   -e USERNAME=$USERNAME \
	   -e PASSWORD=$PASSWORD \
	   -e APP_KEY=$APP_KEY \
	   -e CERT_PATH=/certs \
           -v $(pwd)/certs:/certs \
	   --name betfairstreamer \
	   $CONTAINER_NAME:$TAG_NAME
