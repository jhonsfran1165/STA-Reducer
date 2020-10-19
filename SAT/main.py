import os
from common import config
from settings import loadenv
from bucket import init_bucket
import subprocess
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _create_env(path, mode):
    logging.info('Loading env vars to terraform')
    loadenv(path, mode)
    # TODO: automate this as quick as possible
    # almost impossible to export env vars from python to shell
    # so please, after generate env exec source "sh {}/{}.sh".format(path, mode)
    # os.system("sh {}/{}.sh".format(path, mode))


def _init_pipeline(environment_uid, action):
    logging.info('Configuring cluster to {}'.format(environment_uid))

    path = config()['environments'][environment_uid]['path']
    domain = config()['environments'][environment_uid]['domain']

    _create_env(path, environment_uid)
    _init_backend()

    _terraform_init(path)
    _terraform_validate(path)
    # _terraform_refresh(path, domain)

    path_plan = _terraform_plan(path, environment_uid, domain, action)
    _terraform_apply(path_plan)


def _init_backend():
    logger.info('Start init terraform backend')
    # bucket name
    init_bucket("goodcommerce-k8")


def _terraform_validate(path):
    logger.info('Start validating terraform')
    args_echo = [
        "terraform",
        "validate",
        path
    ]
    subprocess.call(args_echo)


def _terraform_refresh(path, domain):
    logger.info('Start refreshin terraform state')
    args_echo = [
        "terraform",
        "refresh",
        "-var",
        "domain={}".format(domain),
        path
    ]
    subprocess.call(args_echo)


def _terraform_init(path):
    logger.info('Start init terraform')
    args_echo = [
        "terraform",
        "init",
        # reconfigure local state each time
        "-reconfigure",
        path
    ]
    subprocess.call(args_echo)


def _terraform_apply(path_plan):
    logger.info('Applying infrastructure terraform')
    args_echo = [
        "terraform",
        "apply",
        "-auto-approve",
        path_plan
    ]
    subprocess.call(args_echo)


def _terraform_plan(path, mode, domain, action):
    logger.info('Start planing to {} terraform'.format(action))

    args_echo = [
        "terraform",
        "plan",
        "-var",
        "domain={}".format(domain)
    ]

    if action == "destroy":
        path_plan = "{}/{}-destroy.tfplan".format(path, mode)
        args_echo.append("-destroy")
    else:
        path_plan = "{}/{}.tfplan".format(path, mode)

    args_echo.append("-out")
    args_echo.append(path_plan)
    args_echo.append(path)

    subprocess.call(args_echo)
    return path_plan


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    news_domains_choices = list(config()['environments'].keys())

    parser.add_argument(
        'environments',
        help='The new environtment that you want deploy',
        type=str,
        choices=news_domains_choices
    )

    parser.add_argument(
        'option',
        help='do you want destroy the infrastructure?',
        type=str,
        choices=["create", "destroy"]
    )

    args = parser.parse_args()
    _init_pipeline(args.environments, args.option)
