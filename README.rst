A SNS Site for MBAers
=====================


REQURIMENTS
===========
* Python 2.7.5
* Git


INSTALATION
===========
* pip install virtualenv
* mkdir /dir/to/mba/projects/ & cd /dir/to/mba/projects/
* virtualenv mba_env
* source mba_env/scripts/activate(linux) or mba_env/scripts/activate(windows)
* git clone https://github.com/toway/mba.git
* pip install -r requirements.txt
  For Windows user, you should download [py-bcrypt binary][1] first and install it, and remove the package from requirements.txt
* And maybe you need to install the suitable version of kotti_settings, kotti_blog via pip

RUN
====
* pserve development.ini --reload


KNOWN BUGS
==========
* url /admin could not be accessed via kotti0.10a1, but ok for kotti0.10dev,however, kotti0.10dev if not tagged.

[1]: https://bitbucket.org/alexandrul/py-bcrypt/downloads