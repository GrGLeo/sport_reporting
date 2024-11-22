// Code generated by sqlc. DO NOT EDIT.
// versions:
//   sqlc v1.27.0
// source: comments.sql

package database

import (
	"context"
	"database/sql"

	"github.com/google/uuid"
)

const getAllComments = `-- name: GetAllComments :many
SELECT u.username, comment
FROM param.activity_comments as ac
LEFT JOIN settings.users as u
ON u.user_id = ac.user_id
`

type GetAllCommentsRow struct {
	Username sql.NullString
	Comment  string
}

func (q *Queries) GetAllComments(ctx context.Context) ([]GetAllCommentsRow, error) {
	rows, err := q.db.QueryContext(ctx, getAllComments)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var items []GetAllCommentsRow
	for rows.Next() {
		var i GetAllCommentsRow
		if err := rows.Scan(&i.Username, &i.Comment); err != nil {
			return nil, err
		}
		items = append(items, i)
	}
	if err := rows.Close(); err != nil {
		return nil, err
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return items, nil
}

const postComment = `-- name: PostComment :exec
INSERT INTO param.activity_comments(activity_id, user_id, comment)
VALUES (
  $1, $2, $3
)
`

type PostCommentParams struct {
	ActivityID int64
	UserID     uuid.UUID
	Comment    string
}

func (q *Queries) PostComment(ctx context.Context, arg PostCommentParams) error {
	_, err := q.db.ExecContext(ctx, postComment, arg.ActivityID, arg.UserID, arg.Comment)
	return err
}
