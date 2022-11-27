# Canvas 2

Canvas 2 is a full stack web application that was submitted for a group term project. It is based on the Canvas learning management software frequently used in various schools. The main features include user accounts (student, teacher, teaching assistant, admin), course management, assignment management, plagarism detection, an admin panel, and more. Students are able to submit assignments that get checked for plagarism. TAs and teachers are able to grade those assignments and provide feedback. Admins can manage all users and modify courses/assignments, as well as approve new teacher accounts that have been registered. The frontend was built with templated HTML, plain CSS, and plain javascript. The backend was built with Flask and MongoDB.

Some details from the files have been omitted since the database is no longer live.

## Distribution of Work

- azure_agst: Initial project structure, database design, testing, containerization, server configuration
- pv-230: All frontend design (Flask, Jinja2 templates, CSS/JS), testing, contributions to backend development
- shreayp: Integration of plagiarism detection via Jaccard/Simhash algos, testing, contributions to backend development

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
