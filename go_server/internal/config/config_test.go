package config

import (
	"os"
	"testing"
)


func TestIsDocker(t *testing.T) {
  docker := IsDocker()
  if docker == true {
    t.Errorf("Is docker should be false")
  }
}

func TestGetEnvVar(t *testing.T) {
  err := os.Setenv("RUN", "local"); if err != nil {
    t.Error("Set env var failed")
  }

  run_env := GetEnvVar("RUN", "default_value")
  if run_env != "local" {
    t.Errorf("got %q, want %q", run_env, "local")
  }

  run_env = GetEnvVar("UNKNOWN_KEY", "default_value")
  if run_env != "default_value" {
    t.Errorf("got %q, want %q", run_env, "default_value")
  }
}

