# coding: utf-8
# Copyright 2016 Chris Kirkos
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
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from txtelegraf import TelegrafTCPClient, TelegrafUDPClient, Measurement
from twisted.internet.task import deferLater
# from txtelegraf.main import log
from twisted.python import log

import sys
from examples.dummy import dummy_openstack_query


def sendFailed(failure, measurement):
    """ """
    log.err('{measure}'.format(measure=measurement))
    log.err(failure)
    return None


@inlineCallbacks
def writeMeasurements(client):

    for result in dummy_openstack_query:

        name = result['measurement']
        del result['measurement']  # do not break Measurement constructor!
        measurement = Measurement(name, **result)
        log.msg('{data}'.format(data=measurement))

        yield deferLater(reactor, 1, client.sendMeasurement, measurement)\
            .addErrback(sendFailed, measurement)


def main():
    import os
    TELEGRAF_HOST = os.getenv('TELEGRAF_HOST', '127.0.0.1')
    TELEGRAF_TCP_PORT = os.getenv('TELEGRAF_TCP_PORT', 8094)
    TELEGRAF_UDP_PORT = os.getenv('TELEGRAF_UDP_PORT', 8092)

    log.startLogging(sys.stdout)

    client = (len(sys.argv) > 1 and sys.argv[1] == 'udp'
              and TelegrafUDPClient(TELEGRAF_HOST, TELEGRAF_UDP_PORT)) \
        or TelegrafTCPClient(TELEGRAF_HOST, TELEGRAF_TCP_PORT)

    log.msg("Using client {cli}".format(cli=client.__class__.__name__))

    def closeClient(*args):
        return client.close()

    def stopReactor(*args):
        return reactor.stop()

    writeMeasurements(client)\
        .addCallbacks(closeClient, closeClient)\
        .addCallbacks(stopReactor, stopReactor)
    # .addErrback(sendFailed, 'some failure in writeMeasurements')

    reactor.run()


if __name__ == "__main__":
    main()
