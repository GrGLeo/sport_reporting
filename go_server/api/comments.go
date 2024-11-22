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

type CommentResponse struct {
  CommentID int `json:"comment_id"`
  CommentText string `json:"comment_text"`
  Username string `json:"username"`
}

type PostResponse struct {
  Status string `json:"status"`
}

func (cfg *ApiConfig) PostComment (w http.ResponseWriter, r *http.Request) {
  // Verify User authorization
  UserID, err := auth.ValidateRetrieveUser(r.Header, cfg.TokenSecret)
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

func (cfg *ApiConfig) GetAllComments (w http.ResponseWriter, r *http.Request) {
  var AllComments []CommentResponse

  // Verify User authorization
  _, err := auth.ValidateRetrieveUser(r.Header, cfg.TokenSecret)
  if err != nil {
    ResponseWithError(w, 401, err)
    return
  }
  ActivityID, err := strconv.Atoi(r.PathValue("activity_id"))
  CastedActivityID := int64(ActivityID)

  Comments, err := cfg.DBQueries.GetAllComments(r.Context(), CastedActivityID)
  if err != nil {
    ResponseWithError(w, 500, err)
    return
  }

  for _, Comment := range Comments {
  AllComments = append(
    AllComments,
    CommentResponse{
      CommentID: int(Comment.CommentID),
      Username: Comment.Username.String,
      CommentText: Comment.Comment,
    },)
  }

  ResponseWithJson(w, 200, AllComments)
  return
}
