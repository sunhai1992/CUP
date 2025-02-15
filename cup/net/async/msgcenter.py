#!/usr/bin/python
# -*- coding: utf-8 -*
# #############################################################################
#
#  Copyright (c) 2014 Baidu.com,  Inc. All Rights Reserved
#
# #############################################################################
"""
:author:
    Guannan Ma
:create_date:
    2014
:last_date:
    2014
:descrition:
    msg center related module
"""

import time
import threading
import abc

import cup
from cup.net.async import conn


__all__ = ['IMessageCenter']


# pylint: disable=R0921
class IMessageCenter(object):
    """
    Message center class
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, ip, port, thdpool_param=None, stat_intvl=20):
        # super(self.__class__, self).__init__()
        if thdpool_param is None:
            thdpool_param = (3, 5)
        self._conn_mgr = conn.CConnectionManager(
            ip, port, thdpool_param
        )
        self._stop = False
        self._stat_intvl = stat_intvl
        self._stat_cond = threading.Condition()

    def _bind_port(self):
        self._conn_mgr.bind()

    def setup(self):
        """
        setup the message center
        """
        self._bind_port()

    def dump_stat(self):
        """
        dump message center class
        """
        cup.log.info('dump_stat service started')
        while(self._stop is not True):
            time.sleep(10)
            self._stat_cond.acquire()
            self._conn_mgr.dump_stats()
            self._stat_cond.wait(self._stat_intvl)
            self._stat_cond.release()

        cup.log.info('dump_stat service stopped')

    def post_msg(self, msg):
        """
        post a net msg
        """
        self._conn_mgr.push_msg2sendqueue(msg)

    @abc.abstractmethod
    def handle(self, msg):
        """
        handle function which should be implemented by
        sub-class.
        """

    def default_handle(self, msg):  # pylint: disable=W0613,R0201
        """
        default handle for msgcenter
        """
        cup.log.debug('Get a msg that other cannot handle')

    def _run_conn_manager(self):
        self._conn_mgr.poll()

    def is_stopping(self):
        """
        is msg center being stopped
        """
        return self._stop

    def stop(self):
        """
        stop the message center
        """
        cup.log.info('To stop the msgcenter')
        self._conn_mgr.stop()
        self._stop = True
        self._stat_cond.acquire()
        self._stat_cond.notify()
        self._stat_cond.release()
        cup.log.info('msg center stopped')

    def run(self):
        """
        run the msgcenter
        """
        thd_conn_man = threading.Thread(target=self._run_conn_manager, args=())
        thd_conn_man.start()
        thd_stat = threading.Thread(target=self.dump_stat, args=())
        thd_stat.start()
        while not self._stop:
            msg = self._conn_mgr.get_recv_msg()
            if msg is not None:
                self.handle(msg)
                del msg

# vi:set tw=0 ts=4 sw=4 nowrap fdm=indent
