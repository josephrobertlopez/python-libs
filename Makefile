.PHONY: install test clean

install:
	poetry install

test:
	poetry run pytest

behave:
	poetry run behave

run-pomodoro:
	poetry run python src/runners/run.py pomodoro -m 25

clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf build dist

lint:
	poetry run flake8 .
