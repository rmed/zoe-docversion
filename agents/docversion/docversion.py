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
from zoe.deco import *

CONF_FILE = path(env["ZOE_HOME"], "etc", "docversion.conf")
LOG_FILE = path(env["ZOE_HOME"], "etc", "docversion.changes")


@Agent(name="docversion")
class Docversion:

    @Message(tags=["send"])
    def send(self, version, name, sender, to=None):
        """ Send a document to the user or the provided email address. """
        base_path = self.get_path()

        doc_path = path(base_path, name, version)
        if not os.path.isdir(doc_path):
            message = "Didn't find version %s for document %s" % (
                version, name)
            return self.feedback(message, sender, "jabber")

        self.clean_state(sender)

        # Obtain list of files
        flist = sorted(
            [f for f in os.listdir(doc_path) if os.path.isfile(path(doc_path, f))])

        if not flist:
            message = "There are no files for this document in this version"
            return self.feedback(message, sender, "jabber")

        for f in flist:
            state_msg = zoe.MessageBuilder({
                "dst":"relay",
                "relayto":"docversion",
                "sender":sender,
                "tag":"docfile",
                "version":version,
                "name":name,
                "filename":f,
                "to":to or sender
            })

            bus_msg = zoe.MessageBuilder({
                "dst":"relay",
                "tag":"relay",
                "relayto":"jabber",
                "to":sender,
                "msg":f
            })

            # Commands created are the names of the files that are
            # available for the document in the given version.
            zoe.state.Command(sender, f, state_msg)

            self.logger._listener.sendbus(bus_msg.msg())

    @Message(tags=["docfile"])
    def send_file(self, version, name, filename, sender, to):
        """ Send specific document that was chosen by user by introducing
            the filename.
        """
        file_path = path(self.get_path(), name, version, filename)

        if not os.path.isfile(file_path):
            message = "File %s does not exist" % filename
            return self.feedback(message, sender, "jabber")

        attachment = self.create_attachment(file_path)
        subject = "[%s] %s" % (version, name)

        self.clean_state(sender)

        if not to:
            return (
                self.feedback("Sending document...", sender, "jabber"),
                self.feedback(attachment, user, "mail", subject))
        else:
            return (
                self.feedback("Sending document to " + to, sender, "jabber"),
                self.feedback(attachment, to, "mail", subject))


    @Message(tags=["docs"])
    def show_docs(self, sender):
        """ Show versioned documents. """
        base_path = self.get_path()

        doc_list = sorted(os.listdir(base_path))

        return self.feedback("\n".join(doc_list), sender, "jabber")

    @Message(tags=["files"])
    def show_files(self, name, version, sender):
        """ Show the user a list of files por a specific document. """
        doc_path = path(self.get_path(), name, version)

        if not os.path.isdir(doc_path):
            message = "Didn't find version %s for document %s" % (
                version, name)
            return self.feedback(message, sender, "jabber")

        flist = sorted(
            [f for f in os.listdir(doc_path) if os.path.isfile(path(doc_path, f))])

        if not flist:
            message = "There are no files for this document in this version"
            return self.feedback(message, sender, "jabber")

        return self.feedback("\n".join(flist), sender, "jabber")

    @Message(tags=["store"])
    def store(self, version, name, att, sender, docname=None):
        """ Store the document obtained in the attachment. """
        base_path = self.get_path()

        # Create dir if needed
        dir_path = path(base_path, name, version)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

        # We may want to change the destination filename
        dest_path = path(dir_path, docname or os.path.basename(att))
        shutil.move(att, dest_path)

        message = "Added version %s of %s (%s) - by %s\n" % (
            version, name, os.path.basename(dest_path), sender)

        with open(LOG_FILE, "a") as log:
            log.write(message)

        return self.feedback(message, "admin", "jabber")

    @Message(tags=["versions"])
    def versions(self, document, sender):
        """ Tell the sender the versions available for a specific document. """
        base_path = self.get_path()

        doc_path = path(base_path, document)
        if not os.path.isdir(doc_path):
            return self.feedback("Cannot find document", sender, "jabber")

        ver_list = sorted(os.listdir(doc_path))

        return self.feedback("\n".join(ver_list), sender, "jabber")

    def clean_state(self, sender):
        """ Clean temporary state commands. """
        state_path = path(env["ZOE_VAR"], "state", "commands", sender)
        if not os.path.isdir(state_path):
            return

        print("Cleaning temporary state commands")

        for f in os.listdir(state_path):
            try:
                os.remove(path(state_path, f))
            except:
                # No files?
                pass

    def create_attachment(self, dpath):
        """ Create an attachment given the path of the document. """
        with open(dpath, "rb") as doc:
            data = doc.read()

        mime = mimetypes.guess_type(dpath, strict=False)[0]
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
            to_send["att"] = data.str()
            to_send["subject"] = subject

        return zoe.MessageBuilder(to_send)

    def get_path(self):
        """ Get the base path of the document repository. """
        with open(CONF_FILE, "r") as conf:
            base_path = conf.readline().rstrip()

        return base_path
