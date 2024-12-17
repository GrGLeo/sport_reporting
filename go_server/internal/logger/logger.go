package glogger

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"
	"time"
)

// TODO: add filepath and write to json format
type Glogger struct {
  Filepath string
}

type LogEntry struct {
  Level string `json:"level"`
  Time string `json:"time"`
  Method string `json:"method"`
  Url string `json:"url"`
  ClientIP string `json:"client_ip"`
}

func (gl *Glogger) Info (r *http.Request) error{
  now := time.Now().Format("2006-01-02T15:04:05")
  method := strings.ToUpper(r.Method)
  url := r.URL.Path
  clientIP := r.RemoteAddr
  log := fmt.Sprintf("%s |HTTP method: %s |URL: %s |client IP: %s", now, method, url, clientIP)
  fmt.Println(log)

  logEntry := LogEntry{
    Level: "INFO",
    Time: now,
    Method: method,
    Url: url,
    ClientIP: clientIP,
  }

  jsonEntry, err := json.Marshal(logEntry)
  if err != nil {
    return fmt.Errorf("failed to marshal json: %w", err)
  }

  err = gl.AppendToFile(jsonEntry)
  if err != nil {
    return fmt.Errorf("failed to write log: %w", err)
  }
  return nil
}

func (gl *Glogger) AppendToFile(jsonEntry []byte) error {
  f, err := os.OpenFile(gl.Filepath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
  if err != nil {
    return fmt.Errorf("Error while opening file: %w", err)
  }
  defer f.Close()
  
  _, err = f.Write(append(jsonEntry,  '\n'))
  if err != nil {
    return fmt.Errorf("Error writing entry: %w", err)
  }

  return nil
}
