package api

import (
	"fmt"
	"hash/crc32"
	"io"
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
    ResponseWithError(w, 500, err)
    return
  }

  file, header, err := r.FormFile("file")
  defer file.Close()

  fileSize := header.Size

  // Calculate checksum
  hash := crc32.New(crc32.IEEETable)
  _, err = io.Copy(hash, file)
  if err != nil {
    ResponseWithError(w, 500, err)
    return
  }
  checksum := hash.Sum32()
  fmt.Println(fileSize)
  fmt.Println(checksum)
  fmt.Println(UserID)
}
