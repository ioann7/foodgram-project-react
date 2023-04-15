import csv
import logging
from pathlib import Path
from typing import Any, Dict, List

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandParser
from django.db.models import Model

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()

logger = logging.getLogger(__name__)


class CsvToDb:
    """
    To add a new model, write the csv_to_model_name method.
    The order of the methods is important,
    tables will be added in this order.
    """

    @classmethod
    def parse_tables(cls, tables: List[str], path: str) -> None:
        for table in tables:
            file_path = Path(path, f'{table}.csv')
            with open(file_path, encoding='utf-8-sig') as fp:
                reader = csv.reader(fp, delimiter=",", quotechar='"')
                headers: List[str] = next(reader, list())
                data = [
                    {header: row[i] for i, header in enumerate(headers)}
                    for row in reader]
                getattr(cls, f'csv_to_{table}')(data)

    @classmethod
    def get_avaiable_tables(cls) -> List[str]:
        """Returns avaiables tables."""
        result = []
        for key in cls.__dict__.keys():
            if key.startswith('csv_to_'):
                result.append(key.replace('csv_to_', ''))
        return result

    @classmethod
    def sort_tables(cls, tables: List[str]) -> List[str]:
        avaiable_tables = cls.get_avaiable_tables()
        order = {table: i for i, table in enumerate(avaiable_tables)}
        return sorted(tables, key=lambda x: order.get(x, float('inf')))

    @classmethod
    def _save_instance(cls, model_class: Model,
                       instance: Dict[str, str]) -> None:
        obj, status = model_class.objects.get_or_create(**instance)
        created = 'created' if status else 'not created'
        logger.info(f'{model_class.__name__} {obj} is {created}')

    @classmethod
    def csv_to_users(cls, data: List[Dict[str, str]]) -> None:
        for instance in data:
            user = User.objects.create_user(**instance)
            logger.info(f'User {user} is created')

    @classmethod
    def csv_to_ingredients(cls, data: List[Dict[str, str]]) -> None:
        for instance in data:
            cls._save_instance(Ingredient, instance)

    @classmethod
    def csv_to_tags(cls, data: List[Dict[str, str]]) -> None:
        for instance in data:
            cls._save_instance(Tag, instance)

    @classmethod
    def csv_to_recipes(cls, data: List[Dict[str, str]]) -> None:
        for instance in data:
            tags_id = [int(tag) for tag in instance.pop('tags_id').split(',')]
            obj, status = Recipe.objects.get_or_create(**instance)
            if status:
                obj.tags.set(tags_id)
            created = 'created' if status else 'not created'
            logger.info(f'Recipe {obj} is {created}')

    @classmethod
    def csv_to_recipes_ingredients(cls, data: List[Dict[str, str]]) -> None:
        for instance in data:
            ingredient_name = instance.pop('ingredient_name')
            try:
                ingredient = Ingredient.objects.get(name=ingredient_name)
            except Ingredient.DoesNotExists:
                logger.warning(
                    f'RecipeIngredient.'
                    f'Cannot create m2m relation, '
                    f'cause ingredient_name {ingredient_name} does not exists.'
                )
            else:
                instance['ingredient'] = ingredient
                cls._save_instance(RecipeIngredient, instance)


class Command(BaseCommand):
    help = '''
    Fills db from csv.
    Names must be similar to model names.
    '''

    def add_arguments(self, parser: CommandParser) -> None:
        choices = CsvToDb.get_avaiable_tables()
        choices.append('all')
        parser.add_argument(
            'path',
            type=str,
            help='Paste absolute path to the folder with csv files'
        )
        parser.add_argument('tables', nargs='+', type=str,
                            choices=choices, default='all')

    def handle(self, *args: Any, **options: Any) -> str:
        if 'all' in options['tables']:
            tables = CsvToDb.get_avaiable_tables()
        else:
            tables = CsvToDb.sort_tables(options['tables'])
        CsvToDb.parse_tables(tables, options['path'])
        if tables:
            return f'{tables} are added!'
        return 'tables are empty.'
