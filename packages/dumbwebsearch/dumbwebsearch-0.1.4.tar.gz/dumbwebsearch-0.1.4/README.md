# dumb web search

- index a directory of text files in sqlite database
- web browse this directory
- web search this directory with indexed text

## how to run

```
./index.py --docroot /path/to/markdown/dir --database /path/to/database.sqlite index

HTTP_SERVER_BASEURL=/reverse/proxy/subpath HTTP_SERVER_PORT=1234 INDEX_DIR=/path/to/markdown/dir INDEX_DATABASE=/path/to/database.sqlite ./browse.wsgi
```

## requirements

- python3
- sqlite to index/search text
- wsgi to expose said app
- jinja2 + bottle as web framework
- pandoc

## security

- no authentication: put a reverse proxy in front of it with some login
- no optimization for performance: put a reverse proxy to prevent hammering
- pandoc is run to render markdown files, which may have its own problems

## what could be better done

- don't make markdown so much ingrained in this app
