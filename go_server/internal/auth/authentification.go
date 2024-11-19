package auth

import (
	"errors"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

var ErrIncorrect = errors.New("Incorrect password")

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
    if err == bcrypt.ErrMismatchedHashAndPassword {
      return ErrIncorrect
    }
    return err
  }
  return nil
}

func MakeJWT(userID uuid.UUID, TokenSecret string) (string, error) {
  now := time.Now()
  expiresIn := time.Duration(1) * time.Hour
  claims := &jwt.RegisteredClaims{
    Issuer: "endurace",
    IssuedAt: jwt.NewNumericDate(now),
    ExpiresAt: jwt.NewNumericDate(now.Add(expiresIn)),
    Subject: userID.String(),
  }
  token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
  return token.SignedString([]byte(TokenSecret))
}

func ValidateJWT(tokenString, TokenSecret string) (uuid.UUID, error) {
  type claimsStruct struct {
    jwt.RegisteredClaims
  }
  token, err := jwt.ParseWithClaims(
    tokenString,
    &claimsStruct{}, 
    func(token *jwt.Token) (interface{}, error) {return []byte(TokenSecret), nil},
  )
  if err != nil {
    return uuid.Nil, err
  }
  if claims, ok := token.Claims.(*claimsStruct); ok && token.Valid {
    if claims.Issuer != "endurace" {
      return uuid.Nil, errors.New("Invalid issuer")
    }
    userID, err := uuid.Parse(claims.Subject)
    if err != nil {
      return uuid.Nil, err
    }
    return userID, nil
  }
  return uuid.Nil, err
}

func GetBearerToken(header http.Header) (string, error) {
  authorization := header.Get("Authorization")
  if authorization == "" {
    return "", errors.New("No authorization found")
  }
  bearerToken := strings.Split(authorization, " ")
  return bearerToken[1], nil
}

