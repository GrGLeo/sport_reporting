// Code generated by sqlc. DO NOT EDIT.
// versions:
//   sqlc v1.27.0

package database

import (
	"database/sql"
	"time"

	"github.com/google/uuid"
)

type ParamActivityComment struct {
	CommentID  int32
	ActivityID int64
	UserID     uuid.UUID
	Comment    string
}

type SettingsLoginAttempt struct {
	AttemptID   int32
	UserID      uuid.UUID
	Attempts    int32
	LastAttempt time.Time
}

type SettingsUser struct {
	UserID    uuid.UUID
	Username  string
	Password  string
	Email     string
	CreatedAt sql.NullTime
	UpdatedAt sql.NullTime
}
