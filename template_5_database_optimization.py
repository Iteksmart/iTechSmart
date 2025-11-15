"""
Workflow Template #5: Database Performance Optimization
Add this to the workflow_engine.py _load_builtin_templates method
"""

# Add this to the _load_builtin_templates method in workflow_engine.py

self.workflow_templates['database_optimization'] = {
    'name': 'Database Performance Optimization',
    'description': 'Automated database performance tuning workflow',
    'trigger': {
        'type': 'alert',
        'condition': 'query_time > 5 OR connection_pool_usage > 80'
    },
    'steps': [
        {
            'name': 'Identify Slow Queries',
            'action_type': 'command',
            'parameters': {
                'command': 'psql -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"'
            },
            'timeout': 30
        },
        {
            'name': 'Check Connection Pool',
            'action_type': 'command',
            'parameters': {
                'command': 'psql -c "SHOW pool_status;"'
            },
            'condition': 'pool_usage > 80'
        },
        {
            'name': 'Analyze Table Statistics',
            'action_type': 'command',
            'parameters': {
                'command': 'psql -c "SELECT schemaname, tablename, idx_scan FROM pg_stat_user_tables WHERE idx_scan = 0 ORDER BY seq_scan DESC LIMIT 10;"'
            }
        },
        {
            'name': 'Check Table Bloat',
            'action_type': 'command',
            'parameters': {
                'command': 'psql -c "SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||\'.\' ||tablename)) AS size FROM pg_tables WHERE schemaname NOT IN (\'pg_catalog\', \'information_schema\') ORDER BY pg_total_relation_size(schemaname||\'.\' ||tablename) DESC LIMIT 10;"'
            }
        },
        {
            'name': 'Notify DBA Team',
            'action_type': 'notification',
            'parameters': {
                'channels': ['slack', 'email'],
                'message': 'Database performance degradation detected on {host}. Slow queries identified.',
                'severity': 'high'
            }
        },
        {
            'name': 'Wait for Approval',
            'action_type': 'approval',
            'parameters': {
                'timeout': 600,
                'approvers': ['dba-team', 'senior-admin'],
                'message': 'Approve database optimization actions? This will run VACUUM ANALYZE and may cause brief performance impact.'
            }
        },
        {
            'name': 'Run VACUUM ANALYZE',
            'action_type': 'command',
            'parameters': {
                'command': 'psql -c "VACUUM ANALYZE;"'
            },
            'condition': 'approved == true',
            'timeout': 600
        },
        {
            'name': 'Update Statistics',
            'action_type': 'command',
            'parameters': {
                'command': 'psql -c "ANALYZE;"'
            },
            'condition': 'approved == true'
        },
        {
            'name': 'Check Index Usage',
            'action_type': 'command',
            'parameters': {
                'command': 'psql -c "SELECT schemaname, tablename, indexname, idx_scan FROM pg_stat_user_indexes WHERE idx_scan = 0 ORDER BY pg_relation_size(indexrelid) DESC LIMIT 10;"'
            }
        },
        {
            'name': 'Restart Connection Pool',
            'action_type': 'command',
            'parameters': {
                'command': 'systemctl restart pgbouncer'
            },
            'condition': 'pool_issues_persist == true',
            'on_failure': 'Notify Failure'
        },
        {
            'name': 'Wait for Stabilization',
            'action_type': 'wait',
            'parameters': {
                'duration': 30
            }
        },
        {
            'name': 'Verify Performance',
            'action_type': 'check',
            'parameters': {
                'metric': 'average_query_time',
                'condition': '< 2'
            }
        },
        {
            'name': 'Verify Connection Pool',
            'action_type': 'check',
            'parameters': {
                'metric': 'connection_pool_usage',
                'condition': '< 70'
            }
        },
        {
            'name': 'Create Performance Report',
            'action_type': 'log',
            'parameters': {
                'system': 'grafana',
                'type': 'performance_report',
                'details': 'Database optimization completed. Query times improved.'
            }
        },
        {
            'name': 'Log to Database',
            'action_type': 'log',
            'parameters': {
                'system': 'postgresql',
                'type': 'performance_optimization',
                'message': 'Automated optimization workflow completed successfully'
            }
        },
        {
            'name': 'Notify Success',
            'action_type': 'notification',
            'parameters': {
                'channels': ['slack', 'email'],
                'message': '✅ Database optimization completed successfully on {host}. Performance metrics improved.',
                'severity': 'info'
            }
        },
        {
            'name': 'Notify Failure',
            'action_type': 'notification',
            'parameters': {
                'channels': ['slack', 'email', 'pagerduty'],
                'message': '❌ Database optimization failed on {host}. Manual intervention required.',
                'severity': 'critical'
            }
        }
    ]
}