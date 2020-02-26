if [[ ! -d /certs ]]

then
  echo "certificate folder must be in directory"
fi

docker stop betfairstreamer
docker rm betfairstreamer

docker build -t betfairstreamer .

docker run \
-e USERNAME=$USERNAME \
-e PASSWORD=$PASSWORD \
-e APP_KEY=$APP_KEY \
-e CERT_PATH=CERT_PATH \
-v $(pwd):/certs \
--name betfairstreamer \
betfairstreamer
