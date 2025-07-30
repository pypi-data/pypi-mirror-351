#!/usr/bin/env python3
# SPDX-License-Identifier: WTFPL

import argparse
from contextlib import closing
from pathlib import Path
import sqlite3


class Db:
    def __init__(self, docroot):
        self.docroot = docroot
        self.db = None

    def index(self):
        files = {
            sub.name: sub.stat().st_mtime
            for sub in self.docroot.glob("*.md")
        }
        indb = {
            row["filename"]: row
            for row in self.db.execute("SELECT rowid, filename, mtime FROM file")
        }
        rowids = set()
        for name, mtime in files.items():
            if name not in indb:
                rowid = self._indexfile(name)
                rowids.add(rowid)
            else:
                if mtime > indb[name]["mtime"]:
                    self._indexfile(name, indb[name]["rowid"])
                rowids.add(indb[name]["rowid"])
        self.db.executemany(
            """
            DELETE FROM text WHERE rowid = ?
            """,
            [(rowid,) for rowid in {row["rowid"] for row in indb.values()} - rowids]
        )
        self.db.commit()

    def _indexfile(self, name, rowid=None):
        # insert or update returning
        path = self.docroot / name
        mtime = path.stat().st_mtime
        body = path.read_text()
        if rowid is None:
            self.db.execute("INSERT INTO file(filename, mtime) VALUES(?, ?)", (name, mtime))
            ((rowid,),) = self.db.execute("SELECT rowid FROM file WHERE filename = ?", (name,))
            self.db.execute("INSERT INTO text(rowid, body) VALUES(?, ?)", (rowid, body))
        else:
            self.db.execute("UPDATE file SET mtime = ? WHERE rowid = ?", (mtime, rowid))
            self.db.execute("UPDATE text SET body = ? WHERE rowid = ?", (body, rowid))
        return rowid

    def search(self, term):
        for row in self.searchiter(term):
            print("=", row["filename"], "=" * 30)
            print(row[1])
            print()

    def searchiter(self, term):
        for row in self.db.execute(
            """
                SELECT filename, snippet(text, 0, '[', ']', '...', 10)
                FROM text JOIN file ON text.rowid = file.rowid
                WHERE body MATCH ? ORDER BY rank
            """,
            (term,)
        ):
            yield row

    def open(self, dbpath, readonly=False):
        if readonly:
            dbpath = f"file:{dbpath}?mode=ro"
        self.db = sqlite3.connect(dbpath, autocommit=False)
        self.db.row_factory = sqlite3.Row

    def close(self):
        self.db.close()
        self.db = None

    def initdb(self):
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS file(filename TEXT, mtime INTEGER)"
        )
        self.db.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS text USING fts5(body)"
        )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--database", type=Path, default="index.sqlite")
    parser.add_argument("--docroot", type=Path, default=Path.cwd())

    subs = parser.add_subparsers(dest="subcommand", required=True)

    sub = subs.add_parser("index")
    sub.add_argument("--prune", action="store_true")

    sub = subs.add_parser("search")
    sub.add_argument("term")

    args = parser.parse_args()

    db = Db(args.docroot)
    db.open(args.database)
    with closing(db):
        db.initdb()

        if args.subcommand == "search":
            db.search(args.term)
        elif args.subcommand == "index":
            db.index()
        else:
            raise NotImplementedError()


if __name__ == "__main__":
    main()
