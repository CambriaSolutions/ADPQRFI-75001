"""Jinja filters."""
import flask
import jinja2
import pytz

blueprint = flask.Blueprint('filters', __name__)


def _utc_to_pst(utc_dt):
    pst = pytz.timezone('US/Pacific')
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(pst)


@jinja2.contextfilter
@blueprint.app_template_filter()
def utc_to_pst(context, value):
    """Convert a datatime in UTC to PST."""
    return _utc_to_pst(value)


@jinja2.contextfilter
@blueprint.app_template_filter()
def format_dt(context, value):
    """Format a datetime object to be human-readable."""
    return value.strftime('%Y-%m-%d %I:%M %p')
