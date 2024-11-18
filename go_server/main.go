package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"

	"github.com/GrGLeo/sport_reporting/go_server/api"
	"github.com/GrGLeo/sport_reporting/go_server/internal/config"
	"github.com/GrGLeo/sport_reporting/go_server/internal/database"
	_ "github.com/lib/pq"
)

func healthCheck(w http.ResponseWriter, r *http.Request) {
  w.Header().Set("Content-Type", "text/plain; charset=utf-8")
  w.WriteHeader(200)
  w.Write([]byte("Ok"))
}

func main() {
  if !config.IsDocker() {
    config.LoadEnv()
  }

  dbURL := config.GetEnvVar("POSTGRES_URL", "unset")
  TokenSecret := config.GetEnvVar("SECRET", "secret")
  db, err := sql.Open("postgres", dbURL)
  if err != nil {
    log.Fatalf("Error: %v, Shutting down.", err)
  }
  dbQueries := database.New(db)

  mux := http.NewServeMux()
  apiCfg := api.ApiConfig{
    DBQueries: dbQueries,
    TokenSecret: TokenSecret,
  }

 mux.Handle("GET /healthcheck", http.HandlerFunc(healthCheck))
 mux.Handle("POST /users/", http.HandlerFunc(apiCfg.CreateUser))
 mux.Handle("POST /login/", http.HandlerFunc(apiCfg.LogUser))

  server := &http.Server{
    Addr: ":8080",
    Handler: mux,
  }
  if err := server.ListenAndServe(); err != nil {
    fmt.Printf("Error: %q, shutdown.", err)
  }
}
