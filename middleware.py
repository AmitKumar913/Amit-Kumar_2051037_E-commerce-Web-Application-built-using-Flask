import functools
from flask import session,redirect

# middleware auth
def auth(view_func):
    @functools.wraps(view_func)
    def decorated(*args,**kwrags):
        if 'email' not in session:
            return redirect('/')
        return view_func(*args,**kwrags)
    return decorated

def guest(view_func):
    @functools.wraps(view_func)
    def decorated(*args,**kwrags):
        if 'email' in session:
            return redirect('/show_data')
        return view_func(*args,**kwrags)
    return decorated