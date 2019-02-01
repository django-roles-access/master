from django.db import IntegrityError
from django.test import TestCase
from django_roles.models import ViewAccess


class TestViewAccessModel(TestCase):

    def setUp(self):
        self.view_access = ViewAccess(view="namespace:view-name",
                                      type='pu')
        self.view_access.save()

    def test_string_representation(self):
        self.assertEqual(str(self.view_access), "namespace:view-name")

    def test_get_first_objects(self):
        self.assertEqual(ViewAccess.objects.first(), self.view_access)

    def test_count_objects(self):
        self.assertEqual(ViewAccess.objects.count(), 1)

    # Verify model method

    # Verify model attributes
    def test_view_attribute_is_unique(self):
        view_access = ViewAccess(view='namespace:view_name',
                                 type='pu')
        view_access.save()
        view_access2 = ViewAccess(view='namespace:view_name',
                                  type='au')
        with self.assertRaises(IntegrityError):
            view_access2.save()

    def test_view_attribute_is_required(self):
        view_access = ViewAccess()
        view_access.type = 'pu'
        with self.assertRaises(IntegrityError):
            view_access.save()

    def test_type_attribute_is_required(self):
        view_access = ViewAccess()
        view_access.view = 'view-name'
        with self.assertRaises(IntegrityError):
            view_access.save()

    # def test_type_attribute_correct_value(self):
    #     view_access = ViewAccess()
    #     view_access.view = 'view-name'
    #     view_access.type = 'rr'
    #     with self.assertRaises(IntegrityError):
    #         view_access.save()


