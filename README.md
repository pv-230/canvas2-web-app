## Project Description

Canvas 2 seeks to combine Canvas and Turnitin into one sleek web app that professors can use to manage assignments for their classes with plagiarism detection.

## List of Libraries

See `requirements.txt`.

## Setup

- Clone the repo to your location of choice.
- Create a venv using `python3 -m venv .venv`
- Activate the venv using `source .venv/bin/activate`
  - Pro Tip: you can use the `.` shorthand for `source` in some shells
- Install requirements using `pip3 install -r requirements.txt`
- Make sure `.flaskenv` is up to date :)
- Run using `flask run`

## Running

### New! Docker

Users authenticated with the GitHub Container Registry can use our Docker image to get things up and running! Just put all required env vars in `.flaskenv` and run the following command:

```bash
docker run -d --env-file=".flaskenv" -p 5000:5000 [OMITTED]
```

### Development

- Put all env vars in `.flaskenv` then use `flask run`.
  - Flask will load the variables in `.flaskenv` into the session, then launch the generator function in our package's `__init__.py` file

### Production

- `waitress-serve --call 'canvas2:create_app'`
  - Waitress does NOT use `.flaskenv`, but then again all variables that would have been specified in that file should be configured server-side anyway.

## Testing

- Install the `canvas2` package in development mode using `pip3 install -e .`
  - This is the purpose of the `setup.py` file
  - `setup.cfg` is used later in our testing suite to specify vars for pytest and coverage.
- You are now ready to test!
- Then use `pytest` to test the code
  - Pytest will look for any files in `tests/` that begin with `test_`, and then run functions in those files that also begin with that same prefix.
- You can also run coverage tests with `coverage run -m pytest`
  - After running, generate a report using `coverage report`

## References

Icons Used: https://materialdesignicons.com/
