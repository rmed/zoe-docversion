zoe-docversion
==============

A monster agent for managing document versions in my Software Project Management subject.

Notes
-----

- Modify `etc/docversion.conf` in order to specify the path for the "repository"
- In order to have Zoe version a document, send an email with a **single** document attached with the following structure:

```
Subject: Version this

Body:

doc: DOCUMENT_NAME
version: VERSION
file: filename.ext
```

Note that `file` is only used when you want Zoe to store the file you attach with a different name.

- When sending a document, Zoe will show you the list of available files for the specific document in the version provided. Simply type the file name and Zoe will email it to you (or the email you provided).
