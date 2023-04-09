import csv
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand, CommandParser

from recipes.models import Ingredient, Tag

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
    def csv_to_ingredients(cls, data: List[Dict[str, str]]) -> None:
        for instance in data:
            ingredient, status = Ingredient.objects.get_or_create(
                name=instance['name'],
                measurement_unit=instance['measurement_unit'],
            )
            created = 'created' if status else 'not created'
            logger.info(f'Ingredient {ingredient} is {created}')

    @classmethod
    def csv_to_tags(cls, data: List[Dict[str, str]]) -> None:
        for instance in data:
            tag, status = Tag.objects.get_or_create(
                name=instance['name'],
                color=instance['color'],
                slug=instance['slug']
            )
            created = 'created' if status else 'not created'
            logger.info(f'Tag {tag} is {created}')


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
