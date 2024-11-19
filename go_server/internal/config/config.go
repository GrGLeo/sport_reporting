package config

import (
	"log"
	"os"
	"path/filepath"

	"github.com/joho/godotenv"
)


func LoadEnv() {
  parentDir, err := filepath.Abs("../")
  if err != nil {
    log.Fatalf("Error getting the parent directory: %v", err)
  }
  envPath := filepath.Join(parentDir, ".env")
  if _, err := os.Stat(envPath); err == nil {
    err := godotenv.Load(envPath)
    if err != nil {
      log.Fatalf("Error loading .env file")
    }
  }
}

func IsDocker() bool {
  if fileInfo, _ := os.Stat("/.dockerenv"); fileInfo != nil {
    return true
  }
  return false
}

func GetEnvVar(key, defaultValue string) string {
  val := os.Getenv(key)
  if val == "" {
    return defaultValue
  }
  return val
}
