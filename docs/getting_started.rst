.. _getting-started:

Getting Started
===============
1. Install and enable it

   .. code:: bash

       pip install django-workflow


   .. code:: python

       INSTALLED_APPS=[
           ...
           workflow
           ...
       ]

2. Create your first state machine in your model and migrate your db

    .. code:: python

        from django.db import models
        from workflow.models.fields.state import StateField

        class MyModel(models.Model):
            my_state_field = StateField()

3. Create all your ``states`` on the admin page
4. Create a ``workflowmodel`` with your model ( ``MyModel`` - ``my_state_field`` ) information on the admin page
5. Create your ``transition metadata`` within the workflowmodel created earlier, source and destination states
6. Create your ``transition approval metadata`` within the workflowmodel created earlier and authorization rules along with their priority on the admin page
7. Enjoy your ``django-workflow`` journey.

    .. code-block:: python

        my_model=MyModel.objects.get(....)

        my_model.workflow.my_state_field.approve(as_user=transactioner_user)
        my_model.workflow.my_state_field.approve(as_user=transactioner_user, next_state=State.objects.get(label='re-opened'))

        # and much more. Check the documentation

.. note::
    Whenever a model object is saved, it's state field will be initialized with the
    state is given at step-4 above by ``django-workflow``.