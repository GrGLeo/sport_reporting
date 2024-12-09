package api

import (
	"fmt"
	"net/http"

	"github.com/GrGLeo/sport_reporting/go_server/internal/auth"
)

func (cfg *ApiConfig) PostFitFile (w http.ResponseWriter, r *http.Request) {
  UserID, err := auth.ValidateRetrieveUser(r.Header, cfg.TokenSecret)
  if err != nil {
    ResponseWithError(w, 401, err)
    return
  }
  err = r.ParseMultipartForm(10 << 20)
  if err != nil {
    ResponseWithError(w, 401, err)
    return
  }

  file, header, err := r.FormFile("file")
  defer file.Close()

  fileSize := header.Size
  
  fmt.Println(UserID)
}
