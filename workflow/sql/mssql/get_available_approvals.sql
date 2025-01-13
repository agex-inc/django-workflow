WITH approvals_with_min_priority (workflowmodel_id, transition_id, object_id, min_priority) AS
         (
             SELECT workflowmodel_id,
                    transition_id,
                    object_id,
                    min(priority) as min_priority
             FROM workflow.dbo.workflow_transitionapproval
             WHERE workflowmodel_id = '%(workflowmodel_id)s'
               AND status = 'PENDING'
             group by workflowmodel_id, transition_id, object_id
         ),
     authorized_approvals(id, workflowmodel_id, transition_id, source_state_id, object_id, priority) AS
         (
             SELECT ta.id,
                    ta.workflowmodel_id,
                    ta.transition_id,
                    t.source_state_id,
                    ta.object_id,
                    ta.priority
             FROM workflow.dbo.workflow_transitionapproval ta
                      INNER JOIN workflow.dbo.workflow_transition t on t.id = ta.transition_id
                      LEFT JOIN workflow.dbo.workflow_transitionapproval_permissions tap on tap.transitionapproval_id = ta.id
                      LEFT JOIN workflow.dbo.workflow_transitionapproval_groups tag on tag.transitionapproval_id = ta.id
             WHERE ta.workflowmodel_id = '%(workflowmodel_id)s'
               AND ta.status = 'PENDING'
               AND (ta.transactioner_id is null or ta.transactioner_id = '%(transactioner_id)s')
               AND (tap.id is null or tap.permission_id in ('%(permission_ids)s'))
               AND (tag.id is null or tag.group_id in ('%(group_ids)s'))
         ),
     approvals_with_max_priority (id, object_id, source_state_id) AS
         (
             SELECT aa.id, aa.object_id, aa.source_state_id
             FROM approvals_with_min_priority awmp
                      INNER JOIN authorized_approvals aa
                                 ON (
                                         aa.workflowmodel_id = awmp.workflowmodel_id
                                         AND aa.transition_id = awmp.transition_id
                                         AND aa.object_id = awmp.object_id
                                     )

             WHERE awmp.min_priority = aa.priority
         )
SELECT awmp.id
FROM approvals_with_max_priority awmp
         INNER JOIN '%(workflowmodel_object_table)s' wot
                    ON (
                            wot.'%(object_pk_name)s' = awmp.object_id
                            AND awmp.source_state_id = wot.'%(field_name)s'_id
                        )
