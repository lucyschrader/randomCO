# Get a random image from Te Papa
This is a Python application that serves up an image from Te Papa's collections. And then another one. And another. And again...

It uses Te Papa's API, the `askCO` package, and Flask.
* [Te Papa API](https://data.tepapa.govt.nz/docs/)
* [askCO](https://pypi.org/project/askCO/)
* [Flask](https://flask.palletsprojects.com/en/3.0.x/)

## Installation
Clone this repo with `git clone TBD`. In a virtual environment import the `askCO` and `Flask` packages. This should give you `requests` too, but doublecheck.

Register for an API key save it as an environment variable called `TPAK-RANDOM`.

In `app.py` you can set a few config parameters. I recommend keeping `max_records` at 1000 while you're testing it out, as a full object harvest takes a while.

In `random.js` you can set the refresh rate – by default this is 15 seconds.