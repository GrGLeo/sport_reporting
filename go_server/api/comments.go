package api

import (
	"errors"
	"net/http"
	"strconv"

	"github.com/GrGLeo/sport_reporting/go_server/internal/auth"
	"github.com/GrGLeo/sport_reporting/go_server/internal/database"
)


type CommentBody struct {
  CommentText string `json:"comment_text"`
  }

func PostComment(cfg *ApiConfig) (w http.ResponseWriter, r *http.Request) {
  token, err := auth.GetBearerToken(r.Header)
  if err != nil {
    ResponseWithError(w, 401, err)
    return
  }

  UserID, err := auth.ValidateJWT(token, cfg.TokenSecret)
  if err != nil {
    ResponseWithError(w, 401, err)
    return
  }

  // might need to validate the activity_id
  ActivityID, err := strconv.Atoi(r.PathValue("activity_id"))
  ActivityID = int32(ActivityID)
  if err != nil {
    ResponseWithError(w, 500, errors.New("Unable to parse activity_id"))
    return 
    }

  CommentParam := database.PostCommentParams{
    UserID: UserID,
    ActivityID: ActivityID,
    Comment: "",
  }
  err = cfg.DBQueries.PostComment(r.Context(), CommentParam)
  if err != nil {
    ResponseWithError(w, 500, err)
    return
  }
  return
}
