package auth

import (
	"fmt"

	"golang.org/x/crypto/bcrypt"
)


func HashPassword(pwd string) (string, error) {
  hash, err := bcrypt.GenerateFromPassword([]byte(pwd), 1)
  if err != nil {
    fmt.Printf("\nError while encrypting password: %v", err)
    return "", err
  }
  return string(hash), nil
}

func CheckPassword(dbPwd, inputPwd string) error {
  err := bcrypt.CompareHashAndPassword([]byte(dbPwd), []byte(inputPwd))
  if err != nil {
    return err
  }
  return nil
}

