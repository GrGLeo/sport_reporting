-- name: CreateUser :one
INSERT INTO settings.users(user_id, username, password, email, created_at, updated_at)
VALUES (
  gen_random_uuid(), $1, $2, $3, NOW(), NOW()
)
RETURNING user_id, username, email, created_at;

-- name: GetPassword :one
SELECT user_id, password
FROM settings.users
WHERE username = $1;

-- name: GetAttempt :one
SELECT attempts, last_attempt
FROM settings.login_attempts
WHERE user_id = $1;

-- name: CreateAttempt :exec
INSERT INTO settings.login_attempts(user_id, attempts, last_attempt)
VALUES (
  $1, $2, NOW()
);

-- name: UpdateAttempt :exec
UPDATE settings.login_attempts
SET attempts = $1, last_attempt = NOW()
WHERE user_id = $2;

-- name: DeleteAttempt :exec
DELETE FROM settings.login_attempts
WHERE user_id = $1;
