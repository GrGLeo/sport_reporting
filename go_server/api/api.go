package api

import (
	"encoding/json"
	"net/http"

	"github.com/GrGLeo/sport_reporting/go_server/internal/database"
	glogger "github.com/GrGLeo/sport_reporting/go_server/internal/logger"
)


type ApiConfig struct {
  DBQueries *database.Queries
  TokenSecret string
  Logger glogger.Glogger
}

func (cfg *ApiConfig) InfoLog(next http.Handler) http.Handler {
  return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    cfg.Logger.Info(r)
    next.ServeHTTP(w, r)
  })
}


func ResponseWithError(w http.ResponseWriter, code int, err error) {
  w.WriteHeader(code)
  w.Write([]byte(err.Error()))
}


func ResponseWithJson(w http.ResponseWriter, code int, data interface{}) {
  jsonData, err := json.Marshal(data)
  if err != nil {
    ResponseWithError(w, 500, err)
    return
  }
  w.Header().Set("Content-Type", "application/json")
  w.WriteHeader(code)
  w.Write(jsonData)
  return
}
