package api

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"

	"github.com/GrGLeo/sport_reporting/go_server/internal/auth"
	"github.com/GrGLeo/sport_reporting/go_server/internal/database"
)


type CommentBody struct {
  CommentText string `json:"comment_text"`
  }

type PostResponse struct {
  Status string `json:"status"`
}

func (cfg *ApiConfig) PostComment (w http.ResponseWriter, r *http.Request) {
  // Verify authorization
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
  CastedActivityID := int64(ActivityID)
  if err != nil {
    ResponseWithError(w, 500, errors.New("Unable to parse activity_id"))
    return 
    }

  var reqBody CommentBody
  if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
    ResponseWithError(w, 422, errors.New("Invalid JSON"))
    return
  }


  CommentParam := database.PostCommentParams{
    UserID: UserID,
    ActivityID: CastedActivityID,
    Comment: reqBody.CommentText,
  }

  err = cfg.DBQueries.PostComment(r.Context(), CommentParam)
  if err != nil {
    ResponseWithError(w, 500, err)
    return
  }
  ResponseWithJson(w, 200, PostResponse{Status: "Comment posted",})
  return
}
