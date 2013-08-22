from bottle import route, default_app

@route('/')
@view('index.html')
def index():
    return {}

# This must be added in order to do correct path lookups for the views
import os
from bottle import TEMPLATE_PATH
TEMPLATE_PATH.append(os.path.join(os.environ['OPENSHIFT_HOMEDIR'], 
    'runtime/repo/wsgi/views/'))

application=default_app()
