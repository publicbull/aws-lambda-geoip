# -*- coding: utf-8 -*-
import os
from fabric.api import local
from fabric.api import run
from fabric.api import task
from fabric.api import lcd
from fabric_aws_lambda import SetupTask as BaseSetupTask
from fabric_aws_lambda import InvokeTask
from fabric_aws_lambda import MakeZipTask
from fabric_aws_lambda import AWSLambdaInvokeTask
from fabric_aws_lambda import AWSLambdaGetConfigTask
from fabric_aws_lambda import AWSLambdaUpdateCodeTask

BASE_PATH = os.path.dirname(__file__)

LIB_PATH = os.path.join(BASE_PATH, 'lib')
INSTALL_PREFIX = os.path.join(BASE_PATH, 'local')

REQUIREMENTS_TXT = os.path.join(BASE_PATH, 'requirements.txt')

LAMBDA_FUNCTION_NAME = os.path.basename(BASE_PATH)
LAMBDA_HANDLER = 'lambda_handler'
LAMBDA_FILE = os.path.join(BASE_PATH, 'lambda_function.py')

EVENT_FILE = os.path.join(BASE_PATH, 'event.json')

ZIP_FILE = os.path.join(BASE_PATH, 'lambda_function.zip')
ZIP_EXCLUDE_FILE = os.path.join(BASE_PATH, 'exclude.lst')


class SetupTask(BaseSetupTask):
    """Setup on Local Machine"""
    def post_task(self):
        self.install_geolite2()

    def install_geolite2(self):
        local('wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz')
        local('gzip -d GeoLite2-City.mmdb.gz')

@task
def clean():
    for target in [ZIP_FILE, LIB_PATH, INSTALL_PREFIX]:
        local('rm -rf {}'.format(target))

task_setup = SetupTask(
    requirements=REQUIREMENTS_TXT,
    lib_path=LIB_PATH,
    install_prefix=INSTALL_PREFIX
)

task_invoke = InvokeTask(
    lambda_file=LAMBDA_FILE,
    lambda_handler=LAMBDA_HANDLER,
    event_file=EVENT_FILE,
    lib_path=LIB_PATH
)

task_makezip = MakeZipTask(
    zip_file=ZIP_FILE,
    exclude_file=ZIP_EXCLUDE_FILE,
    lib_path=LIB_PATH
)

task_aws_invoke = AWSLambdaInvokeTask(
    function_name=LAMBDA_FUNCTION_NAME,
    payload='file://{}'.format(EVENT_FILE)
)

task_aws_getconfig = AWSLambdaGetConfigTask(
    function_name=LAMBDA_FUNCTION_NAME,
)

task_aws_updatecode = AWSLambdaUpdateCodeTask(
    function_name=LAMBDA_FUNCTION_NAME,
    zip_file='fileb://{}'.format(ZIP_FILE)
)
