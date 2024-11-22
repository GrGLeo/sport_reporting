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
