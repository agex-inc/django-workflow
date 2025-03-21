.. _hooking_function_guide:

.. |Create Function Page| image:: /_static/create-function.png

Functions
=========

Functions are the description in ``Python`` of what you want to do on certain events happen. So you define them once and you can use them
with multiple hooking up. Just go to ``/admin/workflow/function/`` admin page and create your functions there.``django-workflow`` function admin support
python code highlighting as well if you enable the ``codemirror2`` app. Don't forget to collect statics for production deployments.


   .. code:: python

       INSTALLED_APPS=[
           ...
           codemirror2
           workflow
           ...
       ]

Here is an example function;

   .. code:: python

        from datetime import datetime

        def handle(context):
            print(datetime.now())

**Important:** **YOUR FUNCTION SHOULD BE NAMED AS** ``handle``. Otherwise ``django-workflow`` won't execute your function.

|Create Function Page|

Context Parameter
-----------------

``django-workflow`` will pass a ``context`` down to your function in order for you to know why the function is triggered or for which object or so. And the ``context``
will look different for different type of events. But it also has some common parts for all the events. Let's look at how it looks;


``context.hook ->>``

+---------------------+--------+--------------------+---------------------------------------------------------+
|      Key            |  Type  |       Format       |                       Description                       |
+=====================+========+====================+=========================================================+
| type                | String | | * on-approved    | | The event type that is hooked up. The payload will    |
|                     |        | | * on-transit     | | likely differ according to this value                 |
|                     |        | | * on-complete    |                                                         |
+---------------------+--------+--------------------+---------------------------------------------------------+
| when                | String | | * BEFORE         | | Whether it is hooked right before the event happens   |
|                     |        | | * AFTER          | | or right after                                        |
+---------------------+--------+--------------------+---------------------------------------------------------+
| payload             | dict   |                    | | This is the context content that will differ for each |
|                     |        |                    | | event type. The information that can be gotten from   |
|                     |        |                    | | payload is describe in the table below                |
+---------------------+--------+--------------------+---------------------------------------------------------+

Context Payload
---------------

On-Approved Event Payload
^^^^^^^^^^^^^^^^^^^^^^^^^
+---------------------+------------------+---------------------------------------------------------+
|      Key            |  Type            |                       Description                       |
+=====================+==================+=========================================================+
| workflowmodel            | WorkflowModel Model   | The workflowmodel that the transition currently happening    |
+---------------------+------------------+---------------------------------------------------------+
| workflowmodel_object     | | Your WorkflowModel  | | The workflowmodel object of the model that has the state   |
|                     | | Object         | | field in it                                           |
+---------------------+------------------+---------------------------------------------------------+
| transition_approval | | Transition     | | The approval object that is currently approved which  |
|                     | | Approval       | | contains the information of the transition(meta) as   |
|                     |                  | | well as who approved it etc.                          |
+---------------------+------------------+---------------------------------------------------------+

On-Transit Event Payload
^^^^^^^^^^^^^^^^^^^^^^^^
+---------------------+------------------+---------------------------------------------------------+
|      Key            |  Type            |                       Description                       |
+=====================+==================+=========================================================+
| workflowmodel            | WorkflowModel Model   | The workflowmodel that the transition currently happening    |
+---------------------+------------------+---------------------------------------------------------+
| workflowmodel_object     | | Your WorkflowModel  | | The workflowmodel object of the model that has the state   |
|                     | | Object         | | field in it                                           |
+---------------------+------------------+---------------------------------------------------------+
| transition_approval | | Transition     | | The last transition approval object which contains    |
|                     | | Approval       | | the information of the transition(meta) as well as    |
|                     |                  | | who last approved it etc.                             |
+---------------------+------------------+---------------------------------------------------------+


On-Complete Event Payload
^^^^^^^^^^^^^^^^^^^^^^^^^
+---------------------+------------------+---------------------------------------------------------+
|      Key            |  Type            |                       Description                       |
+=====================+==================+=========================================================+
| workflowmodel            | WorkflowModel Model   | The workflowmodel that the transition currently happening    |
+---------------------+------------------+---------------------------------------------------------+
| workflowmodel_object     | | Your WorkflowModel  | | The workflowmodel object of the model that has the state   |
|                     | | Object         | | field in it                                           |
+---------------------+------------------+---------------------------------------------------------+




Example Function
^^^^^^^^^^^^^^^^

   .. code:: python

        from workflow.models.hook import BEFORE, AFTER

        def _handle_my_transitions(hook):
            workflowmodel = hook['payload']['workflowmodel']
            workflowmodel_object = hook['payload']['workflowmodel_object']
            source_state = hook['payload']['transition_approval'].meta.transition_meta.source_state
            destination_state = hook['payload']['transition_approval'].meta.transition_meta.destination_state
            last_approved_by = hook['payload']['transition_approval'].transactioner
            if hook['when'] == BEFORE:
                print('A transition from %s to %s will soon happen on the object with id:%s and field_name:%s!' % (source_state.label, destination_state.label, workflowmodel_object.pk, workflowmodel.field_name))
            elif hook['when'] == AFTER:
                print('A transition from %s to %s has just happened on the object with id:%s and field_name:%s!' % (source_state.label, destination_state.label, workflowmodel_object.pk, workflowmodel.field_name))
            print('Who approved it lately is %s' % last_approved_by.username)

        def _handle_my_approvals(hook):
            workflowmodel = hook['payload']['workflowmodel']
            workflowmodel_object = hook['payload']['workflowmodel_object']
            approved_by = hook['payload']['transition_approval'].transactioner
            if hook['when'] == BEFORE:
                print('An approval will soon happen by %s on the object with id:%s and field_name:%s!' % ( approved_by.username, workflowmodel_object.pk, workflowmodel.field_name ))
            elif hook['when'] == AFTER:
                print('An approval has just happened by %s  on the object with id:%s and field_name:%s!' % ( approved_by.username, workflowmodel_object.pk, workflowmodel.field_name ))

        def _handle_completions(hook):
            workflowmodel = hook['payload']['workflowmodel']
            workflowmodel_object = hook['payload']['workflowmodel_object']
            if hook['when'] == BEFORE:
                print('The workflowmodel will soon be complete for the object with id:%s and field_name:%s!' % ( workflowmodel_object.pk, workflowmodel.field_name ))
            elif hook['when'] == AFTER:
                print('The workflowmodel has just been complete for the object with id:%s and field_name:%s!' % ( workflowmodel_object.pk, workflowmodel.field_name ))

        def handle(context):
            hook = context['hook']
            if hook['type'] == 'on-transit':
                _handle_my_transitions(hook)
            elif hook['type'] == 'on-approved':
                _handle_my_approvals(hook)
            elif hook['type'] == 'on-complete':
                _handle_completions(hook)
            else:
                print("Unknown event type %s" % hook['type'])
