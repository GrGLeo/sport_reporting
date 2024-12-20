package api

import (
	"database/sql"
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
  Email string `json:"email"`
  CreatedAt time.Time `json:"created_at"`
  UpdatedAt time.Time `json:"updated_at"`
  Token string `json:"token"`
}

type LoggedResponse struct {
  Token string `json:"token"`
}

func ResponseLoggedSuccess(w http.ResponseWriter, userID uuid.UUID, tokenSecret string) {
  token, err := auth.MakeJWT(userID, tokenSecret)
  if err != nil {
    ResponseWithError(w, 500, errors.New("Failed to create JWT"))
  }
  response := LoggedResponse{
    Token: token,
  }
  ResponseWithJson(w, 200, response)
  return
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

  token, err := auth.MakeJWT(user.UserID, cfg.TokenSecret)
  if err != nil {
    ResponseWithError(w, 500, errors.New("Failed to create JWT"))
  }

  User := UserResponse{
    Email: user.Email,
    CreatedAt: createdAt,
    Token: token,
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
  userInfo, err := cfg.DBQueries.GetPassword(r.Context(), reqBody.Username)
  if err != nil {
    // User not found
    if err == sql.ErrNoRows {
      ResponseWithError(w, 404, errors.New("user not found."))
      return
    }
    ResponseWithError(w, 500, err)
    return
  }
  attempts, err := cfg.DBQueries.GetAttempt(r.Context(), userInfo.UserID)
  if err != nil {
    if err == sql.ErrNoRows {
      // No attempts are recorded user can login
      err = auth.CheckPassword(userInfo.Password, reqBody.Password)
      if err != nil {
        if errors.Is(err, auth.ErrIncorrect) {
          FirstWrongAttempt := database.CreateAttemptParams{
            UserID: userInfo.UserID,
            Attempts: 1,
          }
          cfg.DBQueries.CreateAttempt(r.Context(), FirstWrongAttempt)
          ResponseWithError(w, 401, err)
          return
        }
        ResponseWithError(w, 500, err)
        return
      }
      ResponseLoggedSuccess(w, userInfo.UserID, cfg.TokenSecret)
      return
    }
    ResponseWithError(w, 500, err)
    return
  }
  // An attempt was made
  if attempts.Attempts == 5 {
    // Checking is user is still locked
    lockedTime := attempts.LastAttempt.Add(1 * time.Minute)
    // TODO: need to fix this time zone issue
    if lockedTime.After(time.Now().Add(60 * time.Minute)) {
      ResponseWithError(w, 401, errors.New("User is locked."))
      return
    // User is unlocked check pwd and reset count to 1 if wrong
    } else {
      err = auth.CheckPassword(userInfo.Password, reqBody.Password)
      if err != nil {
        if errors.Is(err, auth.ErrIncorrect) {
          UpdatedAttempt := database.UpdateAttemptParams{
            UserID: userInfo.UserID,
            Attempts: 1,
          }
          cfg.DBQueries.UpdateAttempt(r.Context(), UpdatedAttempt)
          ResponseWithError(w, 401, err)
          return
        }
        ResponseWithError(w, 500, err)
        return
      }
      cfg.DBQueries.DeleteAttempt(r.Context(), userInfo.UserID)
      ResponseLoggedSuccess(w, userInfo.UserID, cfg.TokenSecret)
      return
    }
  } else {
    err = auth.CheckPassword(userInfo.Password, reqBody.Password)
    if err != nil {
      if errors.Is(err, auth.ErrIncorrect) {
        UpdatedAttempt := database.UpdateAttemptParams{
          UserID: userInfo.UserID,
          Attempts: attempts.Attempts + 1,
        }
        cfg.DBQueries.UpdateAttempt(r.Context(), UpdatedAttempt)
        ResponseWithError(w, 401, err)
        return
      }
      ResponseWithError(w, 500, err)
      return
    }
    cfg.DBQueries.DeleteAttempt(r.Context(), userInfo.UserID)
    ResponseLoggedSuccess(w, userInfo.UserID, cfg.TokenSecret)
    return
  }
}
