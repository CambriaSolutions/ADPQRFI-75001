# -*- coding: utf-8 -*-
"""Application assets."""
import os

from flask_assets import Bundle, Environment
from webassets.filter import get_filter

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
CSS_DIR = os.path.join(BASE_DIR, 'static/css')
BOOTSTRAP_DIR = os.path.join(
    BASE_DIR, 'static/libs/bootstrap-sass/assets/stylesheets')


sass = get_filter('scss', as_output=True,
                  load_paths=(CSS_DIR, BOOTSTRAP_DIR))

css = Bundle(
    'css/bootstrap-editable.css',
    'css/style.scss',
    depends=('css/*.scss'),
    filters=(sass,),
    output='public/css/common.css'
)

js = Bundle(
    'libs/jquery/dist/jquery.js',
    'libs/bootstrap-sass/assets/javascripts/bootstrap.js',
    'js/bootstrap-editable.js',
    'js/plugins.js',
    filters='jsmin',
    output='public/js/common.js'
)

assets = Environment()

assets.register('js_all', js)
assets.register('css_all', css)
