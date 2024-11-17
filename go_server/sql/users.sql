-- name: CreateUser :one
INSERT INTO settings.users(user_id, username, password, email, created_at, updated_at)
VALUES (
  gen_random_uuid(), $1, $2, $3, NOW(), NOW()
)
RETURNING user_id, username, email, created_at;
