#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Zoe Docversion
#
# Copyright (c) 2015 Rafael Medina García <rafamedgar@gmail.com>
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.)

import base64
import mimetypes
import os
import shutil
import zoe
from os import environ as env
from os.path import join as path
from semantic_version import Version
from zoe.deco import *

CONF_FILE = path(env["ZOE_HOME"], "etc", "docversion.conf")
LOG_FILE = path(env["ZOE_HOME"], "etc", "docversion.changes")


@Agent(name="docversion")
class Docversion:

    @Message(tags=["send"])
    def send(self, version, name, filetype, sender, to=None):
        """ Send a document to the user or the provided email address. """
        with open(CONF_FILE, "r") as conf:
            base_path = conf.readline().rstrip()

        doc_path = path(base_path, version, name, "doc." + filetype)
        if not os.path.isfile(doc_path):
            message = "Didn't find version %s for document %s in format %s" % (
                version, name, filetype)
            return self.feedback(message, sender, "jabber")

        attachment = self.create_attachment(doc_path)
        subject = "[%s] %s" % (version, name)

        if not to:
            return (
                self.feedback("Sending document...", sender, "jabber"),
                self.feedback(attachment, user, "mail", subject))
        else:
            return (
                self.feedback("Sending document to " + to, sender, "jabber"),
                self.feedback(attachment, to, "mail", subject))

    @Message(tags=["store"])
    def store(self, version, name, att, sender):
        """ Store the document obtained in the attachment. """
        with open(CONF_FILE, "r") as conf:
            base_path = conf.readline().rstrip()

        # Create dir if needed
        dir_path = path(base_path, version, name)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

        filetype = os.path.splitext(att)[1]

        shutil.move(att, path(dir_path, "doc" + filetype))

        message = "Added version %s of %s (%s) in %s" % (
            version, name, sender, filetype)

        with open(LOG_FILE, "a") as log:
            log.write(message)

        return self.feedback(message, "rafa", "jabber")

    def create_attachment(self, dpath):
        """ Create an attachment given the path of the document. """
        with open(dpath, "rb") as doc:
            data = doc.read()

        mime = mimetypes.guess_type(dpath)
        b64 = base64.standard_b64encode(data).decode("utf-8")

        return zoe.Attachment(b64, mime, os.path.basename(dpath))

    def feedback(self, data, user, relayto, subject=None):
        """ Send feedback to the user

            data -- may be text or an attachment for e-mail
            user -- user to send the feedback to
            relayto -- either 'jabber' or 'mail'
            subject -- subject of the e-mail
        """
        to_send = {
            "dst": "relay",
            "tag": "relay",
            "relayto": relayto,
            "to": user,
        }

        if relayto == "jabber":
            to_send["msg"] = data
        else:
            to_send["html"] = data.str()
            to_send["subject"] = subject

        return zoe.MessageBuilder(to_send)
