from django.test import TestCase

from rossvyaz.models import Phone, Operator, Region


class PhoneTest(TestCase):
    @staticmethod
    def create_phone(begin='9000000000', end='9001000000', operator='Operator', region='Region'):
        o, created = Operator.objects.get_or_create(name=operator)
        r, created = Region.objects.get_or_create(name=region)
        return Phone.objects.create(begin=begin, end=end, operator=o, region=r)

    def test_phone_validation_ok(self):
        pass

    def test_phone_validation_fail(self):
        pass

    def test_phone_find_found(self):
        expected = self.create_phone()
        number_to_find = '9000123456'
        phone = Phone.find(number_to_find)
        self.assertEqual(expected, phone)

    def test_phone_find_fail(self):
        lower = self.create_phone()
        greater = self.create_phone(begin='9990000000', end='9999999999')
        number_to_fail = '9856660205'
        phone = Phone.find(number_to_fail)
        self.assertTrue(phone is None)

    def test_data_loading(self):
        pass
