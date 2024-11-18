-- +goose UP
CREATE SCHEMA IF NOT EXISTS settings;
SET TIME ZONE 'CET';

CREATE TABLE settings.users (
  user_id UUID PRIMARY KEY,
  username VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE settings.login_attempts (
    attempt_id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    last_attempt TIMESTAMP NOT NULL,
    CONSTRAINT fk_user_login_attempts FOREIGN KEY (user_id) REFERENCES settings.users(user_id)
);

-- +goose Down
DROP SCHEMA settings CASCADE;
