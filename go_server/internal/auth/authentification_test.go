package auth

import (
	"testing"

	"github.com/google/uuid"
)

func TestHashPassword(t *testing.T) {
  pwd := "hello"

  hashed, err := HashPassword(pwd)
  if err != nil {
    t.Fatalf("Password was not hashable: %v", err)
  }

  if hashed == pwd {
    t.Error("Password shouldn't be equal to hashed password")
  }

  err = CheckPassword(hashed, pwd) 
  if err != nil {
    t.Error("Password shoud match.")
  } 
}

func TestJWT(t *testing.T) {
  UserID := uuid.New()
  tokenSecret := "secret"

  token, err := MakeJWT(UserID, tokenSecret)
  if err != nil {
    t.Error("Error while making JWT")
  }

  JWTUserId, err := ValidateJWT(token, tokenSecret)
  if err != nil {
    t.Error("Error while validating JWT")
  }
  if UserID != JWTUserId {
    t.Errorf("Got: %q, want: %q", JWTUserId, UserID)
  }
}
