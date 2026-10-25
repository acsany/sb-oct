# Diagrams

Three views of the `second_brain` package, from the code structure down to a
typical session at the terminal.

## 1. Files, functions and imports

How the modules in `src/second_brain/` fit together. Thick arrows are imports
between modules and to external libraries; dotted arrows are function calls.

```mermaid
---
title: second_brain — files, functions and imports
---
flowchart LR
    subgraph entry["Entry points"]
        script[["pyproject.toml<br/>[project.scripts]<br/>second_brain = second_brain.cli:cli"]]
        mainmod[["__main__.py<br/>python -m second_brain"]]
        init[["__init__.py<br/>(empty package marker)"]]
    end

    subgraph cli_py["cli.py — command layer"]
        cli_group("cli()<br/>@click.group")
        cmd_new("new(title, body)")
        cmd_list("list_notes()<br/>command: list")
        cmd_show("show(number)")
    end

    subgraph notes_py["notes.py — note logic"]
        notes_dir("notes_dir()")
        create_note("create_note()")
        split_title_body("split_title_body()")
        clean_block("_clean_block()")
        build_note_path("build_note_path()")
        slugify("slugify()")
        list_note_files("list_note_files()")
        read_note("read_note()")
        default_dir[/"DEFAULT_DIR_NAME"/]
    end

    subgraph app_py["app.py — logging setup"]
        configure_logging("configure_logging()")
        log_file_path("log_file_path()")
        default_log_dir("default_log_dir()")
        stderr_format("stderr_format()")
        level_names[/"LEVEL_SHORT_NAMES"/]
        app_main("main()<br/>@logger.catch<br/>(not used by the CLI)")
    end

    subgraph thirdparty["Third-party"]
        lib_click{{"click"}}
        lib_loguru{{"loguru"}}
        lib_platformdirs{{"platformdirs"}}
    end

    subgraph stdlib["Standard library"]
        std_notes{{"os · re · unicodedata<br/>datetime · pathlib"}}
        std_app{{"sys · os · pathlib"}}
    end

    %% Entry points
    script -->|console script| cli_group
    mainmod ==>|"from second_brain.cli import cli"| cli_group

    %% Imports between modules (thick)
    cli_py ==>|"from second_brain.notes import<br/>create_note, list_note_files,<br/>notes_dir, read_note"| notes_py
    cli_py ==>|"from second_brain.app import<br/>configure_logging"| app_py
    cli_py ==> lib_click
    cli_py ==> lib_loguru
    app_py ==> lib_loguru
    app_py ==> lib_platformdirs
    notes_py ==> std_notes
    app_py ==> std_app

    %% Calls (dotted)
    cli_group -.->|subcommand| cmd_new
    cli_group -.->|subcommand| cmd_list
    cli_group -.->|subcommand| cmd_show
    cli_group -.-> configure_logging
    cmd_new -.-> notes_dir
    cmd_new -.-> create_note
    cmd_list -.-> notes_dir
    cmd_list -.-> list_note_files
    cmd_show -.-> notes_dir
    cmd_show -.-> list_note_files
    cmd_show -.-> read_note
    notes_dir -.-> default_dir
    create_note -.-> split_title_body
    create_note -.-> build_note_path
    split_title_body -.-> clean_block
    build_note_path -.-> slugify
    app_main -.-> configure_logging
    configure_logging -.-> log_file_path
    log_file_path -.-> default_log_dir
    configure_logging -.-> stderr_format
    stderr_format -.-> level_names
```

`app.main()` is left over from the project template: nothing in the CLI calls
it. The CLI only uses `configure_logging()` from `app.py`.

## 2. Entry points and arguments

Both ways of launching the tool end up in the same `cli()` click group, which
sets up logging and then hands over to one of the three commands. Each command
shows its arguments, the functions behind it, and where its output goes.

```mermaid
---
title: second_brain — entry points, arguments and what runs behind them
---
flowchart LR
    subgraph launch["Entry points"]
        console[["second_brain …<br/>console script"]]
        module[["python -m second_brain …<br/>__main__.py"]]
    end

    subgraph group["cli() — click group"]
        root("cli()")
        help_opt["--help<br/>(on cli and every command)"]
        logging("configure_logging()")
    end

    subgraph cmd_new["second_brain new"]
        new_title["TITLE<br/>required"]
        new_body["--body / -b TEXT<br/>optional"]
        new_stdin["--body -<br/>read body from stdin"]
        new_fn("create_note()")
        new_split("split_title_body()<br/>first line → heading<br/>rest → body")
        new_path("build_note_path()<br/>mkdir · slugify ·<br/>-1, -2 … on collision")
        new_out(["stdout: path of new note"])
    end

    subgraph cmd_list["second_brain list"]
        list_noargs["no arguments"]
        list_fn("list_note_files()<br/>*.md, newest first")
        list_missing(["stdout: dir does not exist<br/>exit 0"])
        list_out(["stdout: notes dir +<br/>numbered list"])
    end

    subgraph cmd_show["second_brain show"]
        show_num["NUMBER<br/>required int"]
        show_files("list_note_files()")
        show_check{"dir exists, notes exist,<br/>1 ≤ NUMBER ≤ count?"}
        show_fn("read_note()")
        show_out(["stdout: note markdown"])
        show_err(["stderr: error<br/>exit 1"])
    end

    subgraph storage["Filesystem"]
        notes_store[("notes directory<br/>YYYY-MM-DD-slug.md")]
        log_file[("log file<br/>DEBUG, rotates at 10 MB, keeps 14 days")]
        stderr_sink[("stderr<br/>compact log lines")]
    end

    subgraph env["Environment variables"]
        env_dir[/"SECOND_BRAIN_DIR<br/>default: ~/second_brain/"/]
        env_level[/"LOG_LEVEL<br/>default: INFO"/]
        env_file[/"LOG_FILE<br/>default: app.log in per-user log dir"/]
    end

    console --> root
    module --> root
    root --- help_opt
    root -->|every invocation| logging
    logging --> stderr_sink
    logging --> log_file
    stderr_sink -.-|level| env_level
    log_file -.-|path| env_file
    notes_store -.-|"path via notes_dir()"| env_dir

    root --> new_title & new_body & new_stdin
    new_title & new_body & new_stdin --> new_fn
    new_fn --> new_split --> new_path
    new_path --> new_out
    new_path -->|write UTF-8| notes_store

    root --> list_noargs -->|dir exists| list_fn
    list_noargs -->|dir missing| list_missing
    list_fn --> list_out
    list_fn -->|glob| notes_store

    root --> show_num --> show_files --> show_check
    show_check -->|yes| show_fn --> show_out
    show_check -->|no| show_err
    show_fn -->|read UTF-8| notes_store
```

Results go to stdout and log lines to stderr, so command output can be piped
safely. `--help` is available on the group and on every command.

## 3. Example user flow

A common session: set up once, capture a note, then find and reuse it later.

```mermaid
---
title: Example user flow — capture an idea, find it again later
---
flowchart LR
    start(("Idea!"))

    subgraph setup["1 · One-time setup"]
        sync["uv sync"]
        envq{"Custom notes<br/>folder?"}
        setenv["export SECOND_BRAIN_DIR=~/notes<br/>or cp .env.example .env"]
        help["second_brain --help<br/>learn the commands"]
    end

    subgraph capture["2 · Capture"]
        kind{"How long is<br/>the note?"}
        quick["second_brain new &quot;Caching idea&quot;"]
        multi["second_brain new &quot;Caching idea&quot;<br/>--body &quot;Use an LRU.&quot;"]
        piped["cat draft.md |<br/>second_brain new &quot;Draft&quot; --body -"]
        saved(["prints absolute path<br/>…/second_brain/2026-10-25-caching-idea.md"])
    end

    subgraph find["3 · Find it later"]
        list["second_brain list"]
        listed(["Notes: /Users/you/second_brain<br/>1. 2026-10-25-caching-idea.md<br/>2. 2026-10-24-draft.md"])
        show["second_brain show 1"]
        ok{"exit status 0?"}
        read(["note markdown on stdout<br/># Caching idea …"])
        err(["Error on stderr<br/>e.g. Note 9 not found"])
    end

    subgraph reuse["4 · Reuse"]
        pipe["second_brain show 1 | pbcopy<br/>or open the .md in an editor"]
        done(("Done"))
    end

    start --> sync --> envq
    envq -->|yes| setenv --> help
    envq -->|no, use ~/second_brain| help
    help --> kind

    kind -->|one line| quick
    kind -->|a few lines| multi
    kind -->|a whole file| piped
    quick & multi & piped --> saved

    saved -->|days later| list --> listed -->|pick a number| show --> ok
    ok -->|yes| read --> pipe --> done
    ok -->|no| err -->|check the numbers| list
```
