import os
from bottle import route, default_app, view, run, request
from bottle import TEMPLATE_PATH

@route('/')
@view('index.html')
def index():
	#return '%s\n%s\n%s'% (TEMPLATE_PATH, os.getcwd(), os.path.realpath(__file__))
	path = os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'delme')
	if request.query.write == 'yes':
		try:
			with open(path ,'wb') as f:
				f.write('testing 123\n')
			return {'msg': 'Wrote!'}
		except Exception, e:
			return {'msg': repr(e)}
	else:
		return {'msg': open(path).read()}

try:
	# This must be added in order to do correct path lookups for the views
	TEMPLATE_PATH.append(os.path.join(os.environ['OPENSHIFT_HOMEDIR'], 
	    'app-root/runtime/repo/wsgi/views/'))
except KeyError:
	# Allow this to work locally too.
	print os.path.join(os.getcwd(), 'views/')
	TEMPLATE_PATH.append(os.path.join(os.getcwd(), 'wsgi/views/'))
	run(host='localhost', port=8080, debug=True)

application=default_app()
