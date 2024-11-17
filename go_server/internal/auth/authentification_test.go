package auth

import "testing"

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
