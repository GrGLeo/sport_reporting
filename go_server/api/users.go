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

type LogUserBody struct {
  Username string `json:"username"`
  Password string `json:"password"`
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
  ResponseWithJson(w, 201, User)
  return
}

func (cfg *ApiConfig) LogUser (w http.ResponseWriter, r *http.Request) {
  var reqBody LogUserBody
  if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
    ResponseWithError(w, 422, errors.New("Invalid JSON"))
    return
  }
  
  //TODO: verify if user is locked
  userInfo, err := cfg.DBQueries.GetPassword(r.Context(), reqBody.Username)
  if err != nil {
    ResponseWithError(w, 500, err)
    return
  }

  attempts, err := cfg.DBQueries.GetAttempt(userInfo.UserID)
  if err != nil {
    ResponseWithError(w, 500, err)
    return
  }

  err = auth.CheckPassword(userInfo.Password, reqBody.Password)
  if err != nil {
    // TODO: prevent brute force
    // write on attempt table
    ResponseWithError(w, 401, err)
    return
  }
  w.WriteHeader(200)
  w.Header().Set("Content-Type", "text/plain; charset=utf-8")
  w.Write([]byte("Ok"))
}
