package api

import (
	"encoding/json"
	"errors"
	"net/http"
	"time"

	"github.com/GrGLeo/sport_reporting/go_server/internal/auth"
	"github.com/GrGLeo/sport_reporting/go_server/internal/database"
	"github.com/google/uuid"
)



type CreateUserBody struct {
  Username string `json:"username"`
  Password string `json:"password"`
  Email string `json:"email"`
}

type UserResponse struct {
  ID uuid.UUID `json:"user_id"`
  Username string `json:"username"`
  Email string `json:"email"`
  CreatedAt time.Time `json:"created_at"`
  UpdatedAt time.Time `json:"updated_at"`
}


func (cfg *ApiConfig) CreateUser (w http.ResponseWriter, r *http.Request) {
  var reqBody CreateUserBody
  if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
    ResponseWithError(w, 422, errors.New("Invalid JSON"))
    return
  }

  hashedPassword, err := auth.HashPassword(reqBody.Password)
  if err != nil {
    ResponseWithError(w, 500, errors.New("Error with Password"))
    return
  }

  UserQuery := database.CreateUserParams{
    Username: reqBody.Username,
    Password: hashedPassword,
    Email: reqBody.Email,
  }

  user, err := cfg.DBQueries.CreateUser(r.Context(), UserQuery)
  if err != nil {
    ResponseWithError(w, 404, err)
    return
  }
  var createdAt time.Time
  if user.CreatedAt.Valid {
    createdAt = user.CreatedAt.Time
  } else {
    createdAt = time.Time{}
  }

  User := UserResponse{
    ID: user.UserID,
    Username: user.Username,
    Email: user.Email,
    CreatedAt: createdAt,
  }
  ResponseWithJson(w, 204, User)
  return
}
