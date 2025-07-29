from flask import current_app as app

@app.route('/routes')
def routes():
    return "Routes file here"
