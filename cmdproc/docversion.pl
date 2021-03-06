#!/usr/bin/env perl
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
# SOFTWARE.

use Getopt::Long qw(:config pass_through);

my $send_me;
my $send_to;
my $versions;
my $docs;
my $files;

my $sender;
my @mail;
my @strings;

GetOptions("get" => \$get,
           "run" => \$run,
           "msg-sender-uniqueid=s" => \$sender,
           "sm" => \$send_me,
           "st" => \$send_to,
           "v" => \$versions,
           "d" => \$docs,
           "f" => \$files,
           "mail=s" => \@mails,
           "string=s" => \@strings);


if ($get) {
  &get;
} elsif ($run and $send_me) {
  &send_me;
} elsif ($run and $send_to) {
  &send_to;
} elsif ($run and $versions) {
  &versions;
} elsif ($run and $docs) {
  &docs;
} elsif ($run and $files) {
  &files;
}

#
# Commands in the script
#
sub get {
  print("--sm send me /version <string> /of /document <string>\n");
  print("--st send /version <string> /of /document <string> to <mail>\n");
  print("--v show versions /for <string>\n");
  print("--d show /me /versioned documents\n");
  print("--f show /me files for /document <string> /in /version <string>\n");
}

#
# Send document to sender
#
sub send_me {
  print("message dst=docversion&tag=send&version=$strings[0]&name=$strings[1]&sender=$sender\n");
}

#
# Send document to email
#
sub send_to {
  print("message dst=docversion&tag=send&version=$strings[0]&name=$strings[1]&sender=$sender&to=$mails[0]\n");
}

#
# Show versions of a specific document
#
sub versions {
  print("message dst=docversion&tag=versions&document=$strings[0]&sender=$sender\n");
}

#
# Show versioned documents
#
sub docs {
  print("message dst=docversion&tag=docs&sender=$sender\n");
}

#
# Show files for a specific document in specific version
#
sub files {
  print("message dst=docversion&tag=files&name=$strings[0]&version=$strings[1]&sender=$sender\n");
}
