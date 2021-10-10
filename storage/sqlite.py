"""
use in sqlite as storage backend 
"""
import sqlite3
import json

from results.result import Result

from werkzeug.exceptions import abort


g_schema = """
CREATE TABLE IF NOT EXISTS unresolved (
  template_id INTEGER ,
  input TEXT NOT NULL,
  template TEXT NOT NULL,
  label TEXT NOT NULL,
  context_id TEXT, 
  context_template TEXT,
  analysis TEXT,
  meta JSON,
  context JSON,
  count INTEGER,
  PRIMARY KEY (template_id, context_id)
);

CREATE TABLE IF NOT EXISTS resolved (
  template_id INTEGER ,
  input TEXT NOT NULL,
  template TEXT NOT NULL,
  label TEXT NOT NULL,
  context_id TEXT, 
  context_template TEXT,
  analysis TEXT,
  meta JSON,
  context JSON,
  count INTEGER,
  PRIMARY KEY (template_id, context_id)
);

CREATE TABLE IF NOT EXISTS feedback (
  template_id INTEGER ,
  input TEXT NOT NULL,
  template TEXT NOT NULL,
  label TEXT NOT NULL,
  context_id TEXT, 
  context_template TEXT,
  analysis TEXT,
  meta JSON,
  context JSON,
  count INTEGER,
  PRIMARY KEY (template_id, context_id)
);

"""

g_create_sql = """
INSERT INTO {}  (template_id, input, template, label, analysis, context_id, context_template, meta, context, count) 
 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)  
ON CONFLICT(template_id, context_id) DO UPDATE SET
    input     = excluded.input,
    template  = excluded.template,
    label     = excluded.label,
    analysis  = excluded.analysis,
    meta      = excluded.meta,
    context   = excluded.context,
    count     = excluded.count,
    context_template  = excluded.context_template
"""

class SqliteStore:
    def __init__(self, db_file: str="sqlite3.bin", schema: str = "") -> None:
        self.db = sqlite3.connect(
            db_file,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        self.db.row_factory = sqlite3.Row
        if schema == "":
            schema = g_schema

        self.db.executescript(schema)
        self.db.commit()

    # save into storage  
    def save_unresolved(self, result: Result):
        sql = g_create_sql.format("unresolved")
        self.db.execute(
            sql,  
            (result.template_id, result.input, result.template, result.label, result.analysis, result.context_id, result.context_template, json.dumps(result.meta), json.dumps(result.context), result.count)
        )
        self.db.commit()

    def save_resolved(self, result: Result):
        self.db.execute(
            g_create_sql.format("resolved"),  
            (result.template_id, result.input, result.template, result.label, result.analysis, result.context_id, result.context_template, json.dumps(result.meta), json.dumps(result.context), result.count)
        )
        self.db.commit()

    def save_feedback(self, result: Result):
        self.db.execute(
            g_create_sql.format("feedback"),  
            (result.template_id, result.input, result.template, result.label, result.analysis, result.context_id, result.context_template, json.dumps(result.meta), json.dumps(result.context), result.count)
        )
        self.db.commit()

    # get un resolved results from storage, so user can look at it and take action
    def get_unresolved(self, template_id: int, context_id: str) -> Result:
        unresolved = self.db.execute(
            'SELECT * FROM unresolved WHERE template_id = ? AND context_id = ? ',
            (template_id, context_id)
        ).fetchone()

        if unresolved is None:
            return None

        result = self.get_result_from_sql(unresolved)
        return result

    # get un resolved results from storage, so user can look at it and take action
    def get_resolved(self, template_id: int, context_id: str) -> Result:
        resolved = self.db.execute(
            'SELECT * FROM resolved WHERE template_id = ? AND context_id = ? ',
            (template_id, context_id)
        ).fetchone()

        if resolved is None:
            return None

        result = self.get_result_from_sql(resolved)
        return result

    def get_feedback(self, template_id: int, context_id: str) -> Result:
        feedback = self.db.execute(
            'SELECT * FROM feedback WHERE template_id = ? AND context_id = ? ',
            (template_id, context_id)
        ).fetchone()

        if feedback is None:
            return None

        result = self.get_result_from_sql(feedback)
        return result

    # get all un resolved results from storage, so user can look at it and take action
    def get_all_unresolved(self):
        unresolved = self.db.execute(
            'SELECT * FROM unresolved'
        ).fetchall()


        return [self.get_result_from_sql(i) for i in unresolved ]

    # get all resolved results from storage, could be used for statictics
    def get_all_resolved(self):
        resolved = self.db.execute(
            'SELECT * FROM resolved'
        ).fetchall()

        return [self.get_result_from_sql(i) for i in resolved ]

    # get all results from storage
    def get_all(self):
        return self.get_all_unresolved(), self.get_all_resolved()

    # if user reject the result, means the prediction that the data is 'error' is wrong
    # need to update this result into user feedback, so later prediction can use it as ground truth
    # so it won't be labelled as 'error' again
    # if user accept the result, should mark the result as accepted
    def resolve(self, result: Result):
        self.db.execute(
            'DELETE FROM unresolved WHERE template_id = ? AND context_id = ? ',
            (result.template_id, result.context_id)
        )
        self.db.commit()
        self.db.execute(
            g_create_sql.format("resolved"),  
            (result.template_id, result.input, result.template, result.label, result.analysis, result.context_id, result.context_template, json.dumps(result.meta), json.dumps(result.context), result.count)
        )
        self.db.commit()

    def get_result_from_sql(self, obj:dict) -> Result:
        result = Result(input=obj["input"], template_id=obj["template_id"], template=obj["template"], 
            label=obj["label"], analysis=obj["analysis"], count=obj["count"], context_id=obj["context_id"], context_template=obj["context_template"] 
        )
        try:
            result.meta=json.loads(obj["meta"])
            result.context=json.loads(obj["context"])
        except:
            pass

        return result