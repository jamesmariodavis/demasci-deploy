ABSOLUTE_PATH=$(abspath .)

#####################
# Flask Development #
#####################

# references env variables defined in Dockerfile
.PHONY: flask-server-dev
flask-server-dev:
	export FLASK_APP=${FLASK_APP_FILE_LOCATION} &&\
	export FLASK_ENV=development &&\
	flask run --host=0.0.0.0

# references env variables defined in Dockerfile
.PHONY: flask-server
flask-server:
	export FLASK_APP=${FLASK_APP_FILE_LOCATION} &&\
	flask run --host=0.0.0.0

# references env variables defined in Dockerfile
.PHONY: gunicorn-server
gunicorn-server:
	gunicorn \
	--bind ":${FLASK_APP_PORT}" \
	--workers ${FLASK_APP_WORKERS} \
	--threads ${FLASK_APP_THREADS} \
	--timeout ${FLASK_APP_TIMEOUT} \
	"${FLASK_APP_FILE_LOCATION}:${FLASK_APP_NAME_IN_CODE}"
