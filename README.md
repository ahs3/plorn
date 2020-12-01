# Plorn: Requirements Analysis and Management

Copyright (c) 2020, Al Stone <ahs3@redhat.com>

Everything in this project is licensed under the MIT open source license.

This is an experimental tool for recording and managing requirements used
in specifications.  In particular, this was developed in order to deal with
the requirements being captured to develop a specification for RISC-V
systems.

Requirements are captured in simple YAML (see the `docs` directory for
details on the fields needed).  The `plorn` tool is simple Python that
checks the YAML for desired structure and content -- this is the
`plorn check` command.

The usage model is fairly simple:

* First, create an empty database with `plorn init`; you can either
  provide a data base name -- e.g., plorn.db -- or provide a db entry
  in `~/.plornrc`.

* Now, add requirements.  Write YAML into a file and then add each
  file into the data base with `plorn add filename` (a list of files
  can be provided, too).  Multiple YAML documents per file are also
  allowed.

* That's it.  More features are being added.  The next release
  will allow for generating asciidoc output from the requirements
  in the data base.  At some point, additional analysis will also
  be available.

There is also the `plorn help` command to show what else is available.
