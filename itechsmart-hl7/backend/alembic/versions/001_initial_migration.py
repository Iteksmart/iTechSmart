"""Initial migration - create all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('mrn', sa.String(50), nullable=False, unique=True),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('middle_name', sa.String(100)),
        sa.Column('full_name', sa.String(300)),
        sa.Column('gender', sa.String(20)),
        sa.Column('birth_date', sa.DateTime()),
        sa.Column('ssn', sa.String(11)),
        sa.Column('phone_home', sa.String(20)),
        sa.Column('phone_work', sa.String(20)),
        sa.Column('phone_mobile', sa.String(20)),
        sa.Column('email', sa.String(255)),
        sa.Column('address_line1', sa.String(255)),
        sa.Column('address_line2', sa.String(255)),
        sa.Column('city', sa.String(100)),
        sa.Column('state', sa.String(50)),
        sa.Column('zip_code', sa.String(20)),
        sa.Column('country', sa.String(100)),
        sa.Column('marital_status', sa.String(50)),
        sa.Column('race', sa.String(100)),
        sa.Column('ethnicity', sa.String(100)),
        sa.Column('language', sa.String(50)),
        sa.Column('source_emr', sa.String(50)),
        sa.Column('source_patient_id', sa.String(100)),
        sa.Column('raw_data', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True)
    )
    
    # Create indexes for patients
    op.create_index('idx_patient_mrn', 'patients', ['mrn'])
    op.create_index('idx_patient_name', 'patients', ['last_name', 'first_name'])
    op.create_index('idx_patient_birth_date', 'patients', ['birth_date'])
    op.create_index('idx_patient_source', 'patients', ['source_emr', 'source_patient_id'])
    
    # Create observations table
    op.create_table(
        'observations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('patient_id', sa.String(36), sa.ForeignKey('patients.id'), nullable=False),
        sa.Column('observation_type', sa.String(50)),
        sa.Column('code_system', sa.String(100)),
        sa.Column('code', sa.String(50)),
        sa.Column('code_display', sa.String(255)),
        sa.Column('value_type', sa.String(50)),
        sa.Column('value_quantity', sa.Float()),
        sa.Column('value_string', sa.Text()),
        sa.Column('value_boolean', sa.Boolean()),
        sa.Column('value_code', sa.String(100)),
        sa.Column('unit', sa.String(50)),
        sa.Column('status', sa.String(50)),
        sa.Column('effective_datetime', sa.DateTime()),
        sa.Column('issued_datetime', sa.DateTime()),
        sa.Column('reference_range_low', sa.Float()),
        sa.Column('reference_range_high', sa.Float()),
        sa.Column('reference_range_text', sa.String(255)),
        sa.Column('interpretation_code', sa.String(50)),
        sa.Column('interpretation_display', sa.String(255)),
        sa.Column('abnormal_flag', sa.String(10)),
        sa.Column('source_emr', sa.String(50)),
        sa.Column('source_observation_id', sa.String(100)),
        sa.Column('performer', sa.String(255)),
        sa.Column('raw_data', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create indexes for observations
    op.create_index('idx_observation_patient', 'observations', ['patient_id'])
    op.create_index('idx_observation_type', 'observations', ['observation_type'])
    op.create_index('idx_observation_code', 'observations', ['code'])
    op.create_index('idx_observation_date', 'observations', ['effective_datetime'])
    
    # Create medications table
    op.create_table(
        'medications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('patient_id', sa.String(36), sa.ForeignKey('patients.id'), nullable=False),
        sa.Column('medication_name', sa.String(255)),
        sa.Column('generic_name', sa.String(255)),
        sa.Column('code_system', sa.String(100)),
        sa.Column('code', sa.String(50)),
        sa.Column('dosage_text', sa.Text()),
        sa.Column('strength', sa.String(100)),
        sa.Column('dose_quantity', sa.Float()),
        sa.Column('dose_unit', sa.String(50)),
        sa.Column('route', sa.String(100)),
        sa.Column('frequency', sa.String(100)),
        sa.Column('frequency_code', sa.String(50)),
        sa.Column('status', sa.String(50)),
        sa.Column('intent', sa.String(50)),
        sa.Column('start_date', sa.DateTime()),
        sa.Column('end_date', sa.DateTime()),
        sa.Column('authored_on', sa.DateTime()),
        sa.Column('prescriber_name', sa.String(255)),
        sa.Column('prescriber_id', sa.String(100)),
        sa.Column('pharmacy', sa.String(255)),
        sa.Column('source_emr', sa.String(50)),
        sa.Column('source_medication_id', sa.String(100)),
        sa.Column('raw_data', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create indexes for medications
    op.create_index('idx_medication_patient', 'medications', ['patient_id'])
    op.create_index('idx_medication_name', 'medications', ['medication_name'])
    op.create_index('idx_medication_status', 'medications', ['status'])
    op.create_index('idx_medication_date', 'medications', ['start_date'])
    
    # Create allergies table
    op.create_table(
        'allergies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('patient_id', sa.String(36), sa.ForeignKey('patients.id'), nullable=False),
        sa.Column('allergen', sa.String(255)),
        sa.Column('code_system', sa.String(100)),
        sa.Column('code', sa.String(50)),
        sa.Column('allergy_type', sa.String(50)),
        sa.Column('category', sa.String(50)),
        sa.Column('clinical_status', sa.String(50)),
        sa.Column('verification_status', sa.String(50)),
        sa.Column('criticality', sa.String(50)),
        sa.Column('reaction_manifestation', sa.Text()),
        sa.Column('reaction_severity', sa.String(50)),
        sa.Column('reaction_description', sa.Text()),
        sa.Column('onset_date', sa.DateTime()),
        sa.Column('recorded_date', sa.DateTime()),
        sa.Column('source_emr', sa.String(50)),
        sa.Column('source_allergy_id', sa.String(100)),
        sa.Column('recorder', sa.String(255)),
        sa.Column('raw_data', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create indexes for allergies
    op.create_index('idx_allergy_patient', 'allergies', ['patient_id'])
    op.create_index('idx_allergy_allergen', 'allergies', ['allergen'])
    op.create_index('idx_allergy_criticality', 'allergies', ['criticality'])
    
    # Create hl7_messages table
    op.create_table(
        'hl7_messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('message_type', sa.String(20), nullable=False),
        sa.Column('message_control_id', sa.String(100), nullable=False, unique=True),
        sa.Column('direction', sa.String(10)),
        sa.Column('raw_message', sa.Text(), nullable=False),
        sa.Column('parsed_data', postgresql.JSON()),
        sa.Column('status', sa.String(50)),
        sa.Column('ack_status', sa.String(10)),
        sa.Column('ack_message', sa.Text()),
        sa.Column('patient_id', sa.String(36), sa.ForeignKey('patients.id')),
        sa.Column('patient_mrn', sa.String(50)),
        sa.Column('sending_application', sa.String(100)),
        sa.Column('sending_facility', sa.String(100)),
        sa.Column('receiving_application', sa.String(100)),
        sa.Column('receiving_facility', sa.String(100)),
        sa.Column('connection_id', sa.String(100)),
        sa.Column('error_message', sa.Text()),
        sa.Column('retry_count', sa.Integer(), default=0),
        sa.Column('message_datetime', sa.DateTime()),
        sa.Column('received_at', sa.DateTime(), nullable=False),
        sa.Column('processed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create indexes for hl7_messages
    op.create_index('idx_hl7_message_type', 'hl7_messages', ['message_type'])
    op.create_index('idx_hl7_direction', 'hl7_messages', ['direction'])
    op.create_index('idx_hl7_status', 'hl7_messages', ['status'])
    op.create_index('idx_hl7_patient', 'hl7_messages', ['patient_id'])
    op.create_index('idx_hl7_datetime', 'hl7_messages', ['message_datetime'])
    op.create_index('idx_hl7_connection', 'hl7_messages', ['connection_id'])
    
    # Create emr_connections table
    op.create_table(
        'emr_connections',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('connection_id', sa.String(100), nullable=False, unique=True),
        sa.Column('emr_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('description', sa.Text()),
        sa.Column('config', postgresql.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_connected', sa.Boolean(), default=False),
        sa.Column('last_connection_test', sa.DateTime()),
        sa.Column('last_connection_status', sa.String(50)),
        sa.Column('total_requests', sa.Integer(), default=0),
        sa.Column('successful_requests', sa.Integer(), default=0),
        sa.Column('failed_requests', sa.Integer(), default=0),
        sa.Column('last_request_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(100))
    )
    
    # Create indexes for emr_connections
    op.create_index('idx_connection_type', 'emr_connections', ['emr_type'])
    op.create_index('idx_connection_active', 'emr_connections', ['is_active'])
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_category', sa.String(50)),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('user_id', sa.String(100)),
        sa.Column('username', sa.String(100)),
        sa.Column('user_role', sa.String(50)),
        sa.Column('resource_type', sa.String(50)),
        sa.Column('resource_id', sa.String(100)),
        sa.Column('patient_id', sa.String(36)),
        sa.Column('patient_mrn', sa.String(50)),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('user_agent', sa.String(255)),
        sa.Column('request_method', sa.String(10)),
        sa.Column('request_path', sa.String(500)),
        sa.Column('status', sa.String(50)),
        sa.Column('status_code', sa.Integer()),
        sa.Column('error_message', sa.Text()),
        sa.Column('details', postgresql.JSON()),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('duration_ms', sa.Integer())
    )
    
    # Create indexes for audit_logs
    op.create_index('idx_audit_event_type', 'audit_logs', ['event_type'])
    op.create_index('idx_audit_user', 'audit_logs', ['username'])
    op.create_index('idx_audit_patient', 'audit_logs', ['patient_id'])
    op.create_index('idx_audit_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('emr_connections')
    op.drop_table('hl7_messages')
    op.drop_table('allergies')
    op.drop_table('medications')
    op.drop_table('observations')
    op.drop_table('patients')