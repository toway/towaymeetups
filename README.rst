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
 (For Windows user, you should download [py-bcrypt binary][1] first and install it, and remove the package from requirements.txt)


RUN
====
* pserve development.ini --reload




[1]: https://bitbucket.org/alexandrul/py-bcrypt/downloads