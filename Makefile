DOCKER_CMD := docker-compose
START_YMDH :=

build:
	${DOCKER_CMD} build

run:
	${DOCKER_CMD} run app poetry run python src/main.py -s $(START_YMDH)

run-agg:
	${DOCKER_CMD} run app poetry run python src/agg.py

start-jupyter:
	${DOCKER_CMD} run --service-ports app poetry run jupyter-lab --allow-root --port 10000 --ip=0.0.0.0  --NotebookApp.token='' --notebook-dir=adhock
