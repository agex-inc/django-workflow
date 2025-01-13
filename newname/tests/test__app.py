from django.contrib import admin
from django.test import TestCase
from hamcrest import assert_that, is_not, has_item, instance_of

from newname.admin import OnApprovedHookInline, OnTransitHookInline, OnCompleteHookInline, DefaultWorkflowModelodelAdmin
from newname.models import Function
from newname.tests.admin import BasicTestModelAdmin
from newname.tests.models import BasicTestModel, BasicTestModelWithoutAdmin


class AppTest(TestCase):

    def test__shouldInjectExistingAdminOfTheModelThatHasStateFieldInIt(self):
        assert_that(admin.site._registry[BasicTestModel], instance_of(BasicTestModelAdmin))
        assert_that(admin.site._registry[BasicTestModel].inlines, has_item(OnApprovedHookInline))
        assert_that(admin.site._registry[BasicTestModel].inlines, has_item(OnTransitHookInline))
        assert_that(admin.site._registry[BasicTestModel].inlines, has_item(OnCompleteHookInline))

    def test__shouldInjectADefaultAdminWithTheHooks(self):
        assert_that(admin.site._registry[BasicTestModelWithoutAdmin], instance_of(DefaultWorkflowModelodelAdmin))
        assert_that(admin.site._registry[BasicTestModel].inlines, has_item(OnApprovedHookInline))
        assert_that(admin.site._registry[BasicTestModel].inlines, has_item(OnTransitHookInline))
        assert_that(admin.site._registry[BasicTestModel].inlines, has_item(OnCompleteHookInline))

    def test__shouldNotInjectToAdminOfTheModelThatDoesNotHaveStateFieldInIt(self):
        assert_that(admin.site._registry[Function].inlines, is_not(has_item(OnApprovedHookInline)))
        assert_that(admin.site._registry[Function].inlines, is_not(has_item(OnTransitHookInline)))
        assert_that(admin.site._registry[Function].inlines, is_not(has_item(OnCompleteHookInline)))
