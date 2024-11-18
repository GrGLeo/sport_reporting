FROM golang:1.23-alpine
RUN apk add --no-cache postgresql-client
RUN go install github.com/pressly/goose/v3/cmd/goose@latest
WORKDIR /app
COPY migration /app/migration
RUN chmod +x /app/migration/wait-for-db.sh
ENTRYPOINT ["goose"]
CMD ["--help"]

