# -*- coding: utf-8 -*-
# module storing_render_template.py
#
# Copyright (c) 2021  CorTexT Platform
# Copyright (c) 2021  Cogniteva SAS
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# ---------------------------------------------------------------------------
import pluginlib                                 #
import parscival_plugins.storing                 #
import logging                                   #
log = logging.getLogger(__name__)                #
# ---------------------------------------------------------------------------
from pathlib import Path                         #
import sqlite3                                   #
import contextlib                                #
import mmap                                      #
# ---------------------------------------------------------------------------
class ExecuteSQLiteScript(parscival_plugins.storing.Storer):

  _alias_ = 'storing.binary.execute_sqlite_script'
  _version_ = '1.0.2'

  @staticmethod
  def process(parsing_spec, parsing_data, output_info, **params):
    """process a SQLite script to a binary DB
    """
    # the name of an exising SQLite script
    sqlite_script = output_info['file']

    # check if the SQLite script to process exists and is not empty
    if not sqlite_script.exists() or sqlite_script.stat().st_size == 0:
      log.error("SQLite script '{}' does not exists or is empty".format(str(sqlite_script)))
      return False

    # create a database name foo.sqlite => foo.db
    database_name = str(sqlite_script).removesuffix(output_info['type']) + 'db'
    log.info("Creating database [green]{}[/green]".format(database_name))

    # ensure to start with an empty database file
    open(database_name, 'w').close()

    # execute the script on sqlite_script
    try:
      con = sqlite3.connect(database_name)
      # read the sqlit script
      sqlite_script_file_object= open(sqlite_script, mode="r", encoding="utf8")
      mm = mmap.mmap(sqlite_script_file_object.fileno(), 0, access=mmap.ACCESS_READ)
      with contextlib.closing(mm) as sql_file:
        sql = sql_file.read()
        # shortcut that creates an intermediate cursor object
        # by calling the cursor method, then calls the cursor’s
        # executescript method with the parameters given
        # @see sqlite3.html#sqlite3.Connection.executescript
        con.executescript(sql.decode())
    except sqlite3.Error as e:
      log.error("Error executing SQLite script '{}'".format(sqlite_script.name))
      log.error("Returned error {}".format(e))
      return False

    return True
