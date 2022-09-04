#!/usr/bin/env python

"""
take and parse config file
start backendServer 
start apiserver
"""

from web import app

from web import result

with app.app_context():
    print("run context start backend")
    result.start_backend()

def run():
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5001)


if __name__ == "__main__":
    run()
