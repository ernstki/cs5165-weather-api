from . import j2_functions as functions
#import j2_filters as filters

def register_jinja_helpers(app):
    for func in functions.__all__:
        app.add_template_global(getattr(functions, func))

    # for filter in filters.__all__:
    #    app.add_template_filter(getattr(filters, filter))
