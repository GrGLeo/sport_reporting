FROM golang:1.23-alpine
RUN apk add --no-cache git curl
RUN go install github.com/pressly/goose/v3/cmd/goose@latest
WORKDIR /app
COPY migration /app/migration
ENTRYPOINT ["goose"]
CMD ["--help"]

