# coding: utf-8
# Copyright 2016 Chris Kirkos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (absolute_import, unicode_literals)

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.internet.defer import succeed, Deferred
from twisted.python import log

from txtelegraf.makebytes import b

# import sys
# from twisted.logger import textFileLogObserver, Logger
# log = Logger(observer=textFileLogObserver(sys.stdout))


class TelegrafUDPProtocol(DatagramProtocol):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.closed_d = None

    def startProtocol(self):
        log.msg('<TelegrafUDPProtocol.startProtocol>')
        self.closed_d = Deferred()
        self.transport.connect(self.host, self.port)

    def stopProtocol(self):
        log.msg('<TelegrafUDPProtocol.stopProtocol>')
        self.closed_d.callback(0)

    def write(self, s):
        log.msg('<TelegrafUDPProtocol.write>')
        return self.transport.write(s + b"\n")  # returns bytes sent

    def close(self):
        if self.transport is not None:
            self.transport.loseConnection()
        log.msg('<TelegrafUDPProtocol.close>')
        return self.closed_d


class TelegrafUDPClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.proto = None

    def getConnection(self):
        if self.proto is None:
            self.proto = DatagramProtocol()
            reactor.listenUDP(0, self.proto)

    def sendMeasurement(self, measurement):
        self.getConnection()
        self.proto.transport.write(b(str(measurement)), (self.host, self.port))
        return succeed(1)

    def close(self):
        if self.proto is not None and self.proto.transport is not None:
            self.proto.transport.loseConnection()
        return succeed(1)
