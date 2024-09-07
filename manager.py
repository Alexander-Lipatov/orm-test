import json
import os
from query import Query
from connector import DBConnector
from typing import List


class Manager:
    

    def __init__(self, model_class) -> None:
        self.model_class = model_class
        self._model_fields = self.model_class._original_fields.keys()
        self.q = Query()
        self._connector = DBConnector()


    def fetch(self):
        q = self.q.SELECT(*self._model_fields).FROM(self.model_class._model_name)
        results:List[self.model_class] = []

        q = str(q)
        db_results = self._connector.fetch(q)
        for db_result in db_results:
            model = self.model_class()

            for field_name, field_value in zip(self._model_fields, db_result):
                setattr(model, field_name, field_value)
                # print(field_name, field_value)
            results.append(model)
        return results
    
    def create(self, *args, **kwargs):
        
        columns = [key for key in kwargs.keys()]
        values = [value for value in kwargs.values()]
        q = self.q.INSERT_INTO(self.model_class._model_name, columns, values)
        db_results = self._connector.create(str(q))
        print(db_results)




class MigrationManager:
    def __init__(self, schema_file='schema.json'):
        self.schema_file = schema_file
        self.old_schema = self.load_schema()
    
    def load_schema(self):
        if os.path.exists(self.schema_file):
            with open(self.schema_file, 'r') as f:
                return json.load(f)
        return {}

    def save_schema(self, new_schema):
        with open(self.schema_file, 'w') as f:
            json.dump(new_schema, f)

    def generate_migration(self, current_schema):
        old_schema = self.old_schema
        migrations = []
        
        for model_name, fields in current_schema.items():
            if model_name not in old_schema:
                migrations.append(f"CREATE TABLE {model_name} ({', '.join(fields)});")
            else:
                old_fields = old_schema[model_name]
                for field_name, field_type in fields.items():
                    if field_name not in old_fields:
                        migrations.append(f"ALTER TABLE {model_name} ADD COLUMN {field_name} {field_type};")
        
        return migrations

    def apply_migration(self, migration, db_connection):
        cursor = db_connection.cursor()
        for sql in migration:
            print(sql)
            cursor.execute(sql)
        db_connection.commit()