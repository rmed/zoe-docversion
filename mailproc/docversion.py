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
import email
import re
import sys
from os import environ as env
from os.path import join as path

def parse_mail(mail):
    """ Parse the mail and send info to agent. """
    with open(mail, "r") as f:
        message = email.message_from_file(f)

    # Not valid subject
    if message["Subject"].lower() != "version this":
        return

    # No attachments
    if message.get_content_maintype() != "multipart":
        return

    sender = message["From"]
    body = ""

    for part in message.walk():
        # Body
        if part.get_content_type() == "text/plain":
            body += part.get_payload(decode=True).decode(encoding="utf8")

        # Not an attachment
        if part.get("Content-Disposition") is None:
            continue

        filename = part.get_filename()

        att_path = path(env["ZOE_VAR"], filename)
        with open(att_path, "wb") as att_file:
            att_file.write(part.get_payload(decode=True))

    doc_vers = re.search("doc:(.*)\nversion:(.*)", body, re.IGNORECASE)
    doc = ""
    vers = ""
    if doc_vers:
        print("me")
        doc = doc_vers.group(1).strip()
        vers = doc_vers.group(2).strip()

    print(
        "message dst=docversion&tag=store&sender=%s&att=%s&name=%s&version=%s" % (
            sender, att_path, doc, vers))

if __name__ == "__main__":
    parse_mail(sys.argv[1])
