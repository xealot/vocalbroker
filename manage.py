#!/usr/bin/env python
import site
site.addsitedir('./thirdparty')

from pymysql import install_as_MySQLdb
install_as_MySQLdb()

from django.core.management import execute_manager

from configuration import broker_local

if __name__ == "__main__":
    execute_manager(broker_local)
