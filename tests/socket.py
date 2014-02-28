"""
Copyright (c) 2014, Samsung Electronics Co.,Ltd.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of Samsung Electronics Co.,Ltd..
"""

"""
udt4py - libudt4 Cython-ish wrapper.
URL:                    https://github.com/vmarkovtsev/udt4py
Original author:        Vadim Markovtsev <v.markovtsev@samsung.com>

libudt4 is (c)2001 - 2011, The Board of Trustees of the University of Illinois.
libudt4 URL:            http://udt.sourceforge.net/
"""

"""
UDTSocket tests.
"""


import threading
import time
import unittest
from udt4py import UDTSocket, UDTException


class UDTSocketTest(unittest.TestCase):
    def testOptions(self):
        self.socket = UDTSocket()
        self.assertFalse(self.socket.family_v6)
        self.assertFalse(self.socket.mode_DGRAM)
        self.assertTrue(self.socket.UDT_SNDSYN)
        self.assertTrue(self.socket.UDT_RCVSYN)
        self.assertEqual(65536, self.socket.UDP_SNDBUF)
        self.assertEqual(12288000, self.socket.UDP_RCVBUF)
        self.assertEqual(12058624, self.socket.UDT_SNDBUF)
        self.assertEqual(12058624, self.socket.UDT_RCVBUF)
        self.assertEqual(25600, self.socket.UDT_FC)
        self.socket.UDP_SNDBUF = 1024001
        self.assertEqual(1024001, self.socket.UDP_SNDBUF)

    def testRecvSend(self):
        self.socket = UDTSocket()
        self.assertEqual(UDTSocket.Status.INIT, self.socket.status)
        self.socket.bind("0.0.0.0:7013")
        self.assertEqual(UDTSocket.Status.OPENED, self.socket.status)
        self.assertEqual("0.0.0.0:7013", self.socket.address)
        self.socket.listen()
        self.assertEqual(UDTSocket.Status.LISTENING, self.socket.status)
        other_thread = threading.Thread(target=self.otherConnect)
        other_thread.start()
        sock = self.socket.accept()
        self.assertEqual(UDTSocket.Status.CONNECTED, sock.status)
        self.assertFalse(sock.family_v6)
        self.assertFalse(sock.mode_DGRAM)
        self.assertEqual("127.0.0.1:7013", sock.address)
        self.assertEqual("127.0.0.1", sock.peer_address[0:9])
        msg = bytearray(5)
        sock.recv(msg)
        self.assertEqual(b"hello", msg)
        msg = b"12345"
        sock.recv(msg)
        self.assertEqual(b"hello", msg)
        buf = bytearray(6)
        msg = memoryview(buf)[1:]
        sock.recv(msg)
        self.assertEqual(b"hello", msg)
        other_thread.join()

    def otherConnect(self):
        sock = UDTSocket()
        sock.connect("127.0.0.1:7013")
        self.assertEqual(UDTSocket.Status.CONNECTED, sock.status)
        sock.send(b"hello")
        sock.send(b"hello")
        sock.send(b"hello")

    def testNoBlock(self):
        other_thread = threading.Thread(target=self.otherConnectNoBlock)
        other_thread.start()
        time.sleep(0.1)
        self.socket = UDTSocket(DGRAM=True)
        self.assertTrue(self.socket.mode_DGRAM)
        self.socket.UDT_RCVSYN = False
        self.assertFalse(self.socket.UDT_RCVSYN)
        self.socket.bind("0.0.0.0:7014")
        self.socket.listen()
        sock = None
        while sock is None:
            try:
                sock = self.socket.accept()
            except UDTException as e:
                self.assertEqual(UDTException.EASYNCRCV, e.error_code)
        msg = bytearray(5)
        msg[0] = 0
        while msg[0] == 0:
            try:
                sock.recvmsg(msg)
            except UDTException as e:
                self.assertEqual(UDTException.EASYNCRCV, e.error_code)
        self.assertEqual(b"hello", msg)
        other_thread.join()

    def otherConnectNoBlock(self):
        sock = UDTSocket(DGRAM=True)
        sock.UDT_SNDSYN = False
        self.assertFalse(sock.UDT_SNDSYN)
        while sock.status != UDTSocket.Status.CONNECTED:
            try:
                sock.connect("127.0.0.1:7014")
            except UDTException as e:
                self.assertEqual(UDTException.EASYNCRCV, e.error_code)
        self.assertEqual(UDTSocket.Status.CONNECTED, sock.status)
        sock.sendmsg(b"hello")


if __name__ == "__main__":
    unittest.main()