# -*- coding: utf-8 -*-
"""Application assets."""
import os

from flask_assets import Bundle, Environment
from flask_uploads import IMAGES, UploadSet
from webassets.filter import get_filter

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
CSS_DIR = os.path.join(BASE_DIR, 'static/css')
BOOTSTRAP_ASSETS_DIR = os.path.join(
    BASE_DIR, 'static/libs/bootstrap-sass/assets')
BOOTSTRAP_CSS_DIR = os.path.join(
    BOOTSTRAP_ASSETS_DIR, 'stylesheets')


sass = get_filter('scss',
                  load_paths=(CSS_DIR, BOOTSTRAP_CSS_DIR))

bootstrap = Bundle(
    'css/bootstrap-editable.css',
    'css/style.scss',
    depends=('css/*.scss'),
    filters=(sass,),
    output='public/css/common.css'
)

css = Bundle(
    bootstrap,
    depends=('css/*.css'),
    filters='cssmin',
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

uploads = UploadSet('uploads', IMAGES,
                    default_dest=lambda app: os.path.join(app.static_folder, 'uploads'))
