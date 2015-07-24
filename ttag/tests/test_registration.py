from django import template
from django.test import TestCase

import ttag


class RegisterTest(TestCase):

    def test_names(self):
        register = template.Library()

        class Registration(ttag.Tag):
            pass

        class CamelCaseRegistration(ttag.Tag):
            pass

        class AlternateNameRegistration(ttag.Tag):

            class Meta:
                name = 'alt_name_registration'

        register.tag(Registration)
        register.tag(CamelCaseRegistration)
        register.tag(AlternateNameRegistration)

        self.assertEqual(len(register.tags), 3)
        self.assertTrue('registration' in register.tags)
        self.assertTrue('camel_case_registration' in register.tags)
        self.assertTrue('alt_name_registration' in register.tags)
