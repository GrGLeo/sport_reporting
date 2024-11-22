-- name: PostComment :exec 
INSERT INTO param.activity_comments(activity_id, user_id, comment)
VALUES (
  $1, $2, $3
);

-- name: GetAllComments :many
SELECT comment_id, u.username, comment
  
FROM param.activity_comments as ac
LEFT JOIN settings.users as u
ON u.user_id = ac.user_id
WHERE activity_id = $1;

-- name: UpdateComment :exec
UPDATE param.activity_comments
SET comment = $1
WHERE comment_id = $2
AND activity_id = $3;

-- name: DeleteComment :exec
DELETE FROM param.activity_comments
WHERE comment_id = $1
AND activity_id = $2;
