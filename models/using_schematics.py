# coding=utf-8
import datetime

from schematics.models import Model
from schematics.types import StringType, DecimalType, DateTimeType, BaseType


class CapStringType(StringType):
    def to_native(self, value, context=None):
        if not value:
            return ''

        parts = value.split()
        return ' '.join([p.capitalize() for p in parts if p])

    def to_primitive(self, value, context=None):
        return value.lower() if value else None


class WeatherReport(Model):
    city = StringType()
    temperature = DecimalType()
    taken_at = DateTimeType(default=datetime.datetime.now)


class Person(Model):
    name = CapStringType()
    zipcode = StringType(min_length=6, max_length=6)


if __name__ == '__main__':
    # t1 = WeatherReport({'city': 'NYC', 'temperature': 80})
    # print(t1.validate())
    # t1.taken_at = 'some'
    # print(t1.validate())

    # p = Person({'name': 'a', 'zipcode': '12345'})
    # p.validate()

    p = Person({'name': 'steve    jobs', 'zipcode': None})
    print(p.to_native())
    print(p.to_primitive())

    p = Person({'name': None, 'zipcode': None})
    print(p.to_native())
    print(p.to_primitive())
