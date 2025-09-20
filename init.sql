-- GUVNL Queue Management System - Database Initialization and Seed Data

-- Load main schema
\i schema.sql

-- Insert default system settings
INSERT INTO settings (key, value, description, is_public) VALUES
    ('system_name', 'GUVNL Queue Management System', 'System display name', TRUE),
    ('max_advance_booking_days', '30', 'Maximum days in advance for booking', TRUE),
    ('default_appointment_duration', '30', 'Default appointment duration in minutes', TRUE),
    ('notification_advance_minutes', '15', 'Minutes before appointment to send reminder', FALSE),
    ('max_appointments_per_day', '100', 'Maximum appointments per day per service', FALSE),
    ('system_timezone', 'Asia/Kolkata', 'System timezone', TRUE),
    ('working_hours_start', '09:00', 'Standard office opening time', TRUE),
    ('working_hours_end', '17:00', 'Standard office closing time', TRUE),
    ('lunch_break_start', '13:00', 'Lunch break start time', TRUE),
    ('lunch_break_end', '14:00', 'Lunch break end time', TRUE);

-- Insert default offices
INSERT INTO offices (name, code, address, city, state, postal_code, phone, email) VALUES
    ('GUVNL Head Office', 'GUVNL-HO', 'Sardar Patel Vidyut Bhavan, Race Course, Vadodara', 'Vadodara', 'Gujarat', '390007', '+91-265-2355501', 'info@guvnl.com'),
    ('GUVNL Ahmedabad Division', 'GUVNL-AHM', 'Urja Bhavan, Gandhinagar Road, Ahmedabad', 'Ahmedabad', 'Gujarat', '380009', '+91-79-23254800', 'ahmedabad@guvnl.com'),
    ('GUVNL Surat Division', 'GUVNL-SRT', 'Vidyut Bhavan, VIP Road, Surat', 'Surat', 'Gujarat', '395007', '+91-261-2463200', 'surat@guvnl.com'),
    ('GUVNL Rajkot Division', 'GUVNL-RJT', 'Urja Bhavan, University Road, Rajkot', 'Rajkot', 'Gujarat', '360005', '+91-281-2471200', 'rajkot@guvnl.com');

-- Insert default services
INSERT INTO services (name, description, estimated_duration, category, required_documents) VALUES
    ('New Electricity Connection', 'Apply for new residential/commercial electricity connection', 45, 'Connection Services', '["Identity Proof", "Address Proof", "Property Documents", "Load Requirements"]'),
    ('Bill Payment and Queries', 'Electricity bill payment and related queries', 15, 'Billing Services', '["Consumer Number", "Previous Bill"]'),
    ('Load Enhancement', 'Increase sanctioned load for existing connection', 30, 'Connection Services', '["Consumer Number", "Load Enhancement Application", "Electrical Installation Certificate"]'),
    ('Meter Replacement', 'Replace faulty or damaged electricity meter', 30, 'Technical Services', '["Consumer Number", "Complaint Number", "Previous Meter Reading"]'),
    ('Complaint Registration', 'Register complaints for power outages, billing issues, etc.', 20, 'Customer Services', '["Consumer Number", "Issue Description"]'),
    ('Subsidy and Scheme Applications', 'Apply for various government electricity subsidy schemes', 35, 'Government Schemes', '["Income Certificate", "Category Certificate", "Consumer Details"]'),
    ('Name Transfer and Address Change', 'Transfer connection to new owner or update address', 40, 'Administrative Services', '["Transfer Deed", "New Owner ID", "NOC from Previous Owner"]'),
    ('Disconnection and Reconnection', 'Temporary or permanent disconnection/reconnection services', 25, 'Connection Services', '["Consumer Number", "Request Application", "Clearance Certificate"]');

-- Link services to all offices (in real scenario, this might vary)
INSERT INTO office_services (office_id, service_id, is_available)
SELECT o.id, s.id, TRUE
FROM offices o
CROSS JOIN services s;

-- Insert default admin user
INSERT INTO users (email, phone, password_hash, first_name, last_name, role, is_active, is_verified) VALUES
    ('admin@guvnl.com', '+919876543210', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqyJMgLy3YqGJZZ5x1x1x1x', 'System', 'Administrator', 'super_admin', TRUE, TRUE),
    ('staff@guvnl.com', '+919876543211', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqyJMgLy3YqGJZZ5x1x1x1x', 'Staff', 'User', 'staff', TRUE, TRUE),
    ('demo@citizen.com', '+919876543212', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqyJMgLy3YqGJZZ5x1x1x1x', 'Demo', 'Citizen', 'citizen', TRUE, TRUE);

-- Assign staff to offices
INSERT INTO staff_assignments (user_id, office_id, assigned_by)
SELECT 
    (SELECT id FROM users WHERE email = 'staff@guvnl.com'),
    o.id,
    (SELECT id FROM users WHERE email = 'admin@guvnl.com')
FROM offices o;

-- Create sample queues for today and tomorrow
INSERT INTO queues (office_id, service_id, queue_date, status, max_tokens)
SELECT 
    o.id,
    s.id,
    CURRENT_DATE,
    'active',
    CASE 
        WHEN s.name LIKE '%Bill Payment%' THEN 150  -- Higher capacity for bill payments
        WHEN s.name LIKE '%New Electricity%' THEN 50  -- Lower capacity for complex services
        ELSE 100
    END
FROM offices o
CROSS JOIN services s;

-- Create queues for tomorrow as well
INSERT INTO queues (office_id, service_id, queue_date, status, max_tokens)
SELECT 
    o.id,
    s.id,
    CURRENT_DATE + INTERVAL '1 day',
    'active',
    CASE 
        WHEN s.name LIKE '%Bill Payment%' THEN 150
        WHEN s.name LIKE '%New Electricity%' THEN 50
        ELSE 100
    END
FROM offices o
CROSS JOIN services s;

-- Create some sample appointments for demonstration
DO $$
DECLARE
    demo_user_id UUID;
    queue_record RECORD;
    token_counter INTEGER;
BEGIN
    -- Get demo user ID
    SELECT id INTO demo_user_id FROM users WHERE email = 'demo@citizen.com';
    
    token_counter := 1;
    
    -- Create sample appointments for today
    FOR queue_record IN 
        SELECT id FROM queues 
        WHERE queue_date = CURRENT_DATE 
        LIMIT 10
    LOOP
        INSERT INTO appointments (
            user_id, 
            queue_id, 
            token_number, 
            appointment_date,
            appointment_time,
            status
        ) VALUES (
            CASE WHEN token_counter <= 3 THEN demo_user_id ELSE NULL END,
            queue_record.id,
            token_counter,
            CURRENT_DATE,
            ('09:00:00'::time + (token_counter * interval '30 minutes'))::time,
            CASE 
                WHEN token_counter = 1 THEN 'completed'::appointment_status
                WHEN token_counter = 2 THEN 'in_progress'::appointment_status
                WHEN token_counter <= 5 THEN 'confirmed'::appointment_status
                ELSE 'scheduled'::appointment_status
            END
        );
        
        -- Update queue current token number
        UPDATE queues 
        SET current_token_number = GREATEST(current_token_number, 
            CASE 
                WHEN token_counter <= 2 THEN token_counter 
                ELSE current_token_number 
            END)
        WHERE id = queue_record.id;
        
        token_counter := token_counter + 1;
    END LOOP;
END $$;

-- Insert sample queue metrics
INSERT INTO queue_metrics (
    queue_id, 
    metric_date, 
    total_appointments, 
    completed_appointments, 
    cancelled_appointments,
    average_wait_time,
    average_service_time,
    peak_hour_start,
    peak_hour_end
)
SELECT 
    q.id,
    CURRENT_DATE - INTERVAL '1 day',
    FLOOR(RANDOM() * 50 + 20)::INTEGER,
    FLOOR(RANDOM() * 40 + 15)::INTEGER,
    FLOOR(RANDOM() * 5)::INTEGER,
    RANDOM() * 30 + 10,
    s.estimated_duration + RANDOM() * 10,
    '11:00:00'::time,
    '12:00:00'::time
FROM queues q
JOIN services s ON q.service_id = s.id
WHERE q.queue_date = CURRENT_DATE
LIMIT 20;

-- Create indexes for better performance on commonly queried data
CREATE INDEX IF NOT EXISTS idx_queues_date_status ON queues(queue_date, status);
CREATE INDEX IF NOT EXISTS idx_appointments_date_status ON appointments(appointment_date, status);
CREATE INDEX IF NOT EXISTS idx_appointments_user_date ON appointments(user_id, appointment_date);

-- Create a view for queue status summary
CREATE OR REPLACE VIEW queue_status_summary AS
SELECT 
    q.id as queue_id,
    o.name as office_name,
    s.name as service_name,
    q.queue_date,
    q.status as queue_status,
    q.current_token_number,
    q.max_tokens,
    COUNT(a.id) as total_appointments,
    COUNT(CASE WHEN a.status = 'completed' THEN 1 END) as completed_appointments,
    COUNT(CASE WHEN a.status = 'in_progress' THEN 1 END) as in_progress_appointments,
    COUNT(CASE WHEN a.status IN ('scheduled', 'confirmed') THEN 1 END) as pending_appointments,
    COALESCE(AVG(CASE WHEN a.actual_wait_time IS NOT NULL THEN a.actual_wait_time END), 0) as avg_wait_time
FROM queues q
JOIN offices o ON q.office_id = o.id
JOIN services s ON q.service_id = s.id
LEFT JOIN appointments a ON q.id = a.queue_id
GROUP BY q.id, o.name, s.name, q.queue_date, q.status, q.current_token_number, q.max_tokens;

-- Create a view for user appointment history
CREATE OR REPLACE VIEW user_appointment_history AS
SELECT 
    a.id as appointment_id,
    u.first_name || ' ' || u.last_name as user_name,
    u.email,
    u.phone,
    o.name as office_name,
    s.name as service_name,
    a.token_number,
    a.appointment_date,
    a.appointment_time,
    a.status,
    a.estimated_wait_time,
    a.actual_wait_time,
    a.created_at as booking_time
FROM appointments a
LEFT JOIN users u ON a.user_id = u.id
JOIN queues q ON a.queue_id = q.id
JOIN offices o ON q.office_id = o.id
JOIN services s ON q.service_id = s.id;

COMMIT;