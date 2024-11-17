// Code generated by sqlc. DO NOT EDIT.
// versions:
//   sqlc v1.27.0

package database

import (
	"database/sql"

	"github.com/google/uuid"
)

type SettingsLoginAttemtp struct {
	AttemptID   int32
	UserID      uuid.UUID
	Attempts    sql.NullInt32
	LastAttempt sql.NullTime
	IsLocked    sql.NullBool
}

type SettingsUser struct {
	UserID    uuid.UUID
	Username  string
	Password  string
	Email     string
	CreatedAt sql.NullTime
	UpdatedAt sql.NullTime
}
