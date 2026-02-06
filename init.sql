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


DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'job_order_status') THEN
    CREATE TYPE public.job_order_status AS ENUM ('NEW', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
  END IF;
END$$;

-- 2) customers
CREATE TABLE IF NOT EXISTS public.customers (
  cust_id bigserial PRIMARY KEY,
  cust_name text NOT NULL,
  cust_email text NOT NULL,
  deleted_at timestamptz NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS customers_email_active_uk
ON public.customers (lower(cust_email))
WHERE deleted_at IS NULL;

-- 3) jobs
CREATE TABLE IF NOT EXISTS public.jobs (
  job_id bigserial PRIMARY KEY,
  job_title text NOT NULL,
  CONSTRAINT jobs_title_uk UNIQUE (job_title)
);

-- 4) job_orders
CREATE TABLE IF NOT EXISTS public.job_orders (
  job_order_id bigserial PRIMARY KEY,
  cust_id int8 NOT NULL,
  job_id int8 NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  status public.job_order_status NOT NULL DEFAULT 'NEW',
  customer_note text,

  CONSTRAINT job_orders_cust_id_fkey
    FOREIGN KEY (cust_id)
    REFERENCES public.customers(cust_id)
    ON DELETE RESTRICT,

  CONSTRAINT job_orders_job_id_fkey
    FOREIGN KEY (job_id)
    REFERENCES public.jobs(job_id)
    ON DELETE RESTRICT
);


INSERT INTO public.customers (cust_name, cust_email, deleted_at) VALUES
('Alice Morgan', 'alice.morgan@example.com', NULL),
('Bob Smith', 'bob.smith@example.com', NULL),
('Charlie Brown', 'charlie.brown@example.com', NULL),
('Diana Prince', 'diana.prince@example.com', NULL),
('Ethan Hunt', 'ethan.hunt@example.com', NULL);


INSERT INTO public.jobs (job_title) VALUES
('Water Tank Cleaning'),
('Air Conditioner Maintenance'),
('Electrical System Inspection'),
('Plumbing Repair'),
('General Home Maintenance');


INSERT INTO public.job_orders (cust_id, job_id, status, customer_note) VALUES
(1, 1, 'NEW', 'First order from Alice'),
(2, 2, 'NEW', 'Urgent request from Bob'),
(3, 3, 'IN_PROGRESS', 'Work started for Charlie'),
(4, 4, 'COMPLETED', 'Finished job for Diana'),
(5, 5, 'CANCELLED', 'Order cancelled by Ethan');


