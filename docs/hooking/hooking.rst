.. _hooking_guide:

Hook it Up
==========

The hookings in ``django-workflow`` can be created both specifically for a workflowmodel object or for a whole workflowmodel. ``django-workflow`` comes with some model objects and admin interfaces which you can use
to create the hooks.

* To create one for whole workflowmodel regardless of what the workflowmodel object is, go to

    * ``/admin/workflow/onapprovedhook/`` to hook up to an approval
    * ``/admin/workflow/ontransithook/`` to hook up to a transition
    * ``/admin/workflow/oncompletehook/`` to hook up to the completion of the workflowmodel

* To create one for a specific workflowmodel object you should use the admin interface for the workflowmodel object itself. One amazing feature of ``django-workflow`` is now that
it creates a default admin interface with the hookings for your workflowmodel model class. If you have already defined one, ``django-workflow`` enriches your already defined
admin with the hooking section. It is default disabled. To enable it just define ``Workflow_INJECT_MODEL_ADMIN`` to be ``True`` in the ``settings.py``.


**Note:** They can programmatically be created as well since they are model objects. If it is needed to be at workflowmodel level, just don't provide the workflowmodel object column. If it is needed
to be for a specific workflowmodel object then provide it.

Here are the list of hook models;

* OnApprovedHook
* OnTransitHook
* OnCompleteHook
