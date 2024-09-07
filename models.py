import sys
from typing import Dict, List
from collections import OrderedDict
from manager import Manager, MigrationManager
from connector import DBConnector


class ModelRegistry:
    _models = []

    @classmethod
    def register_model(cls, model_class):
        cls._models.append(model_class)

    @classmethod
    def get_registered_models(cls):
        return cls._models


class Field:
    pass


class IntegerField(Field):
    pass


class CharField(Field):
    pass


class ModelMeta(type):

    _original_fields = None
    


    def __new__(mcs, class_name, parents, attributes: Dict[str, str | Field]):
        
        fields = OrderedDict()
        for attr_key, attr_value in attributes.items():
            if isinstance(attr_value, Field):
                fields[attr_key] = attr_value
                attributes[attr_key] = None
        c = super(ModelMeta, mcs).__new__(mcs, class_name, parents, attributes)
        # ct = c.create_table(attributes['__qualname__'].lower())
        setattr(c, '_model_name', attributes['__qualname__'].lower())
        setattr(c, '_original_fields', fields)
        setattr(c, 'objects', Manager(c))

        # if c._model_name != 'model':

        ModelRegistry.register_model(c)

        # Генерация схемы таблицы
        current_schema = {c._model_name: {key: type(field).__name__ for key, field in fields.items()}}
        setattr(c, '_current_schema', current_schema)

        return c
    

class Model(metaclass=ModelMeta):
    objects:Manager

class UserModel(Model):
    name = CharField()
    age = IntegerField()
    password = IntegerField()

    
class PostModel(Model):
    title = CharField()

class CommentModel(Model):
    text = CharField()
    post_id = IntegerField()
    user_id = IntegerField()


def gen_migrate():
    if len(sys.argv) > 1 and sys.argv[1] == 'migrate':

     # Создание экземпляра менеджера миграций
        migration_manager = MigrationManager()

        # Получение всех зарегистрированных моделей
        models = ModelRegistry.get_registered_models()
        
        # Генерация схем для всех моделей
        current_schema = {}
        for model in models:
            current_schema.update(model._current_schema)
        
        # Генерация миграций на основе изменений
        migration = migration_manager.generate_migration(current_schema)
        
        if migration:
            print("Найдены миграции:")
            for sql in migration:
                print(sql)
            # Применение миграции к базе данных (здесь просто вывод для примера)
            migration_manager.apply_migration(migration, DBConnector()._conn)
        else:
            print("Миграций не найдено")

        # Сохранение текущей схемы
        migration_manager.save_schema(current_schema)

if __name__ == '__main__':
    gen_migrate()
    