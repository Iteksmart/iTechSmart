"""
Workflow Template #5: Database Performance Optimization
Add this to the workflow_engine.py _load_builtin_templates method
"""

# Add this to the _load_builtin_templates method in workflow_engine.py

# workflow_templates["database_optimization"] = {
#     "name": "Database Performance Optimization",
#     "description": "Automated database performance tuning workflow",
#     "category": "database",
#     "version": "1.0.0",
#     "steps": [
#         {
#             "name": "analyze_database_performance",
#             "description": "Analyze current database performance metrics",
#             "tool": "database_analyzer",
#             "parameters": {
#                 "analysis_type": "performance_audit",
#                 "include_recommendations": True
#             },
#             "required": True
#         },
#         {
#             "name": "identify_slow_queries",
#             "description": "Identify and analyze slow queries",
#             "tool": "query_optimizer",
#             "parameters": {
#                 "threshold_ms": 1000,
#                 "analyze_execution_plans": True
#             },
#             "required": True
#         },
#         {
#             "name": "optimize_indexes",
#             "description": "Optimize database indexes based on usage patterns",
#             "tool": "index_optimizer",
#             "parameters": {
#                 "analyze_missing_indexes": True,
#                 "suggest_removals": True
#             },
#             "required": False
#         },
#         {
#             "name": "update_statistics",
#             "description": "Update database statistics for better query planning",
#             "tool": "database_maintenance",
#             "parameters": {
#                 "operation": "update_statistics"
#             },
#             "required": False
#         },
#         {
#             "name": "generate_report",
#             "description": "Generate optimization report",
#             "tool": "report_generator",
#             "parameters": {
#                 "report_type": "performance_optimization",
#                 "include_recommendations": True
#             },
#             "required": True
#         }
#     ],
#     "parameters": {
#         "target_database": {
#             "type": "string",
#             "description": "Target database name",
#             "required": True
#         },
#         "performance_threshold": {
#             "type": "number",
#             "description": "Performance threshold in milliseconds",
#             "default": 1000,
#             "required": False
#         }
#     },
#     "output_schema": {
#         "performance_metrics": {
#             "type": "object",
#             "description": "Database performance analysis results"
#         },
#         "optimization_recommendations": {
#             "type": "array",
#             "description": "List of optimization recommendations"
#         },
#         "implemented_changes": {
#             "type": "array",
#             "description": "List of changes implemented"
#         }
#     }
# }
