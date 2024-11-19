package glogger

import (
	"fmt"
	"net/http"
	"strings"
	"time"
)

// TODO: add filepath and write to json format
type Glogger struct {
}

func (gl *Glogger) Info (r *http.Request) {
  now := time.Now().Format("2006-01-02T15:04:05")
  method := strings.ToUpper(r.Method)
  url := r.URL.Path
  clientIP := r.RemoteAddr
  fmt.Printf("\n%s |HTTP method: %s |URL: %s |client IP: %s", now, method, url, clientIP)
}

