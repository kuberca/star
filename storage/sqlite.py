"""
use in sqlite as storage backend 
"""
import sqlite3
import json
from typing import List

from results.result import Result
from results.result import Group

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
  group_id INTEGER ,
  error_type TEXT,
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
  group_id INTEGER ,
  error_type TEXT,
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
  group_id INTEGER ,
  error_type TEXT,
  PRIMARY KEY (template_id, context_id)
);

CREATE TABLE IF NOT EXISTS groups (
  group_id INTEGER PRIMARY KEY,
  vector TEXT NOT NULL, 
  count INTEGER,
  manual_group BOOLEAN, 
  deleted BOOLEAN DEFAULT 0,
  error_type TEXT
);

"""

g_create_sql = """
INSERT INTO {}  (template_id, input, template, label, analysis, context_id, context_template, meta, context, count, group_id, error_type)
 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)  
ON CONFLICT(template_id, context_id) DO UPDATE SET
    input     = excluded.input,
    template  = excluded.template,
    label     = excluded.label,
    analysis  = excluded.analysis,
    meta      = excluded.meta,
    context   = excluded.context,
    count     = excluded.count,
    group_id  = excluded.group_id,
    context_template  = excluded.context_template,
    error_type = excluded.error_type
"""

g_create_group_sql = """
INSERT INTO groups (group_id, vector, count, manual_group, error_type)
    VALUES (?, ?, ?, ?, ?)
ON CONFLICT(group_id) DO UPDATE SET
    vector        = excluded.vector,
    count         = excluded.count,
    manual_group  = excluded.manual_group,
    error_type    = excluded.error_type

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
            (result.template_id, result.input, result.template, result.label, result.analysis, result.context_id, result.context_template, 
                json.dumps(result.meta), json.dumps(result.context), result.count, result.group_id, result.error_type)
        )
        self.db.commit()

    def save_resolved(self, result: Result):
        self.db.execute(
            g_create_sql.format("resolved"),  
            (result.template_id, result.input, result.template, result.label, result.analysis, result.context_id, result.context_template, 
                json.dumps(result.meta), json.dumps(result.context), result.count, result.group_id, result.error_type)
        )
        self.db.commit()

    def save_feedback(self, result: Result):
        self.db.execute(
            g_create_sql.format("feedback"),  
            (result.template_id, result.input, result.template, result.label, result.analysis, result.context_id, result.context_template, 
                json.dumps(result.meta), json.dumps(result.context), result.count, result.group_id, result.error_type)
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
            (result.template_id, result.input, result.template, result.label, result.analysis, 
            result.context_id, result.context_template, json.dumps(result.meta), json.dumps(result.context), 
            result.count, result.group_id, result.error_type)
        )
        self.db.commit()

    def get_result_from_sql(self, obj:dict) -> Result:
        result = Result(input=obj["input"], template_id=obj["template_id"], template=obj["template"], 
            label=obj["label"], analysis=obj["analysis"], count=obj["count"], context_id=obj["context_id"], 
            context_template=obj["context_template"], group_id=obj["group_id"], error_type=obj["error_type"]
        )
        try:
            result.meta=json.loads(obj["meta"])
            result.context=json.loads(obj["context"])
        except:
            pass

        return result


    # save group into storage, return the generated group_id
    def save_group(self, group: Group) -> Group:
        if  group.group_id == 0:
            cur  = self.db.execute(
                "INSERT INTO groups (vector, count, manual_group, error_type) VALUES (?, ?, ?, ?)",
                (group.vector_str(), group.count, group.manual_group, group.error_type)
            )
            group.group_id = cur.lastrowid
            return group
        else:
            self.db.execute(
                g_create_group_sql,
                (group.group_id, group.vector_str(), group.count, group.manual_group, group.error_type)
            )
            return group

    # get group from storage
    def get_group(self, group_id: int) -> Group:
        group = self.db.execute(
            'SELECT * FROM groups WHERE group_id = ? ',
            (group_id,)
        ).fetchone()

        if group is None:
            return None

        return self.get_group_from_sql(group)

    # get all group not deleted from storage
    def get_groups(self) -> List[Group]:
        groups = self.db.execute(
            'SELECT * FROM groups where deleted = 0'
        ).fetchall()

        return [self.get_group_from_sql(g) for g in groups]

    # get groups with results
    def get_groups_with_results(self) -> List[Group]:
        groups = self.db.execute(
            'SELECT * FROM groups'
        ).fetchall()
        
        g_all = []
        for g in groups:
            g = self.get_group_from_sql(g)
            results = self.get_group_results(g.group_id)
            if len(results) > 0:
                g.results = results
                g_all.append(g)

        return g_all

    # get group with results
    def get_group_with_results(self, group_id: int) -> Group:
        group = self.db.execute(
            'SELECT * FROM groups WHERE group_id = ? ',
            (group_id,)
        ).fetchone()

        if group is None:
            return None

        g = self.get_group_from_sql(group)
        g.results = self.get_group_results(g.group_id)
        return g

    # get all results of a  group
    def get_group_results(self, group_id: int) -> List[Group]:
        unresolved = self.db.execute(
            'SELECT * FROM unresolved WHERE group_id = ?',
            (group_id,)
        ).fetchall()

        return [self.get_result_from_sql(i) for i in unresolved ]

    # get Group object from select result
    def get_group_from_sql(self, obj:dict) -> Group:
        if obj is None:
            return None
        return Group(group_id=obj["group_id"], vector_str=obj["vector"], count=obj["count"], manual_group=obj["manual_group"], error_type=obj["error_type"])

    # change results group_id from old_group_id to new_group_id
    def change_group(self, old_group_id: int, new_group_id: int):
        self.db.execute(
            'UPDATE unresolved SET group_id = ? WHERE group_id = ?',
            (new_group_id, old_group_id)
        )
        self.db.commit()    

    # mark a group as deleted
    def delete_group(self, group_id: int):
        self.db.execute(
            'UPDATE groups SET deleted = 1 WHERE group_id = ?',
            (group_id,)
        )
        self.db.commit()

    # cleanup delete all groups and results
    def cleanup(self):
        self.db.execute(
            'DELETE FROM unresolved'
        )
        self.db.execute(
            'DELETE FROM resolved'
        )
        self.db.execute(
            'DELETE FROM groups'
        )
        self.db.commit()
