CREATE TABLE IF NOT EXISTS service_requests (
  id SERIAL PRIMARY KEY,
  description TEXT NOT NULL,
  customer_name TEXT NOT NULL,
  customer_email TEXT NOT NULL
);

INSERT INTO service_requests (description, customer_name, customer_email)
VALUES
 ('Replace ATM receipt printer', 'Alice Brown', 'alice@example.com'),
 ('Investigate cash dispenser jam', 'Bob Smith', 'bob@example.com'),
 ('Software update on kiosk', 'Alice Brown', 'alice@example.com');

