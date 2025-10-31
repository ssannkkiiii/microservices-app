FROM golang:1.21-alpine

WORKDIR /app

RUN go mod init translate-worker
RUN go get github.com/rabbitmq/amqp091-go

COPY app.go .

RUN go build -o worker app.go

CMD ["./worker"]
