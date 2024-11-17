package main

import (
  "net/http"
  "fmt"
)

func main() {
  server := &http.Server{
    Addr: ":8080",
  //  Handler: mux,
  }
  if err := server.ListenAndServe(); err != nil {
    fmt.Printf("Error: %q, shutdown.", err)
  }
}
