package api

import "net/http"


type CommentBody struct {
  ActivityID int `json:"activity_id"`
  CommentText string `json:"comment_text"`
  }

func PostComment(cfg *ApiConfig) (w http.ResponseWriter, r *http.Request) {

  return
}
