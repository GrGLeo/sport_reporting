-- +goose UP
CREATE SCHEMA IF NOT EXISTS param;

CREATE TABLE param.activity_comments (
  comment_id SERIAL PRIMARY KEY,
  activity_id BIGINT NOT NULL,
  user_id UUID NOT NULL,
  comment TEXT NOT NULL DEFAULT '',
  -- CONSTRAINT fk_activity FOREIGN KEY (activity_id) REFERENCES activities(activity_id) ON DELETE CASCADE,
  CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES settings.users(user_id) ON DELETE CASCADE
);

-- +goose Down
DROP SCHEMA param CASCADE;
