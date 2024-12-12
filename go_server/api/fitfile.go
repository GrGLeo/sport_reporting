package api

import (
	"net/http"

	"github.com/GrGLeo/sport_reporting/go_server/internal/auth"
	"github.com/GrGLeo/sport_reporting/go_server/internal/protocol"
)

func (cfg *ApiConfig) PostFitFile (w http.ResponseWriter, r *http.Request) {
  UserID, err := auth.ValidateRetrieveUser(r.Header, cfg.TokenSecret)
  if err != nil {
    ResponseWithError(w, 401, err)
    return
  }
  err = r.ParseMultipartForm(10 << 20)
  if err != nil {
    ResponseWithError(w, 500, err)
    return
  }

  file, header, err := r.FormFile("file")
  defer file.Close()

  fileSize := header.Size

  fs := protocol.FileSender{
    File: file,
    UserID: UserID,
    FileSize: int(fileSize),
    TransactionID: 1,
  }
  fs.SendFile()
  return
}
