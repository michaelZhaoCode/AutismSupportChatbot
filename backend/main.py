"""
app.py

This module serves as the entry point for running the Flask application.

Imports:
    from api import app: Imports the Flask application instance from the api module.

Execution:
    If this module is executed as the main program, it runs the Flask application in debug mode.
"""
from api.app import app

if __name__ == '__main__':
    app.run(debug=True)
