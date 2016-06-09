Cambria Solutions OSI Prototype
===============================

A flask app.


Quickstart
----------

If using a Cloud9 workspace, create a new workspace with the following Github
repository and the name 'adpqrfi-75001':

    https://github.com/CambriaSolutions/ADPQRFI-75001

If NOT using Cloud9, manually clone the repository:

    git clone https://github.com/CambriaSolutions/ADPQRFI-75001

Run the following command to install
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):

    sudo pip3 install virtualenvwrapper

Add the following to ``.bashrc`` or ``.bash_profile`` from the terminal. You will
need to use ``nano ~/.bashrc`` or ``vi ~/.bashrc`` to edit it.

    export OSI_PROTOTYPE_SECRET='something-really-secret'
    export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh

You will need to open a new terminal to see the changes take effect.

Then run the following commands to bootstrap your environment with Python 3 and
all development requirements.

    sudo gem install bundle
    bundle install
    mkvirtualenv proto
    workon proto
    pip install -r requirements/dev.txt

Run the following to create your app's database tables and perform the initial migration:

    python manage.py db upgrade
    python manage.py seed

If all this succeeds, you can start the server by running the following command:

    python manage.py server

Substitute your username into this URL to view the running app:

    https://adpqrfi-75001-{your cloud9 username}.c9users.io/

For instance, my webserver would be running at:

    https://adpqrfi-75001-indraastra.c9users.io/

Whenever you open a new terminal, you'll need to run this command to use
python properly:

    workon proto


Shell
-----

To open the interactive shell, run ::

    python manage.py shell

By default, you will have access to ``app``, ``db``, and the ``User`` model.


Running Tests
-------------

To run all tests, run:

    python manage.py test

To run the code linter, run:

    python manage.py lint


Migrations
----------

Whenever a database migration needs to be made. Run the following commands:

    python manage.py db migrate

This will generate a new migration script. Then run:

    python manage.py db upgrade

To apply the migration.

For a full migration command reference, run ``python manage.py db --help``.


Deployment
----------

After committing your changes, simply push them to Github and Travis will re-run the tests in a sandbox and deploy to Heroku if 
successful:

    git commit -m "Some new changes"
    git push origin master
