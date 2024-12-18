package api

import (
	"bytes"
	"fmt"
	"io"
	"math/rand"
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
  
  // We copy the file to a byte.Buffer to be able to reset the pointer
  var buf bytes.Buffer
  _, err = io.Copy(&buf, file)
  if err != nil {
    fmt.Println("Error copying file to buffer:", err)
    http.Error(w, "Failed to process file", http.StatusInternalServerError)
    return
    }

  fs := protocol.FileSender{
    File: buf,
    UserID: UserID,
    FileSize: int(fileSize),
    TransactionID: uint16(rand.Int()),
    PacketMap: make(map[int][]byte),
  }
  fs.SendFile()
  return
}
