package protocol

import (
	"hash/crc32"
	"io"

	"github.com/google/uuid"
)

const (
  ProtocolVersion = 1
  MaxPacketSize = 1024
  ServerAddress = "localhost:8090"
)

type InitPacket struct {
  MessageType uint8
  TransactionID uint16
  FileSize uint32
  Checksum uint32
  UUID uuid.UUID
}

type Header struct {
  MessageType uint8
  TransactionID uint16
  FileSize uint32
  Checksum uint32
}

type FileSender struct {
  File []byte
  userID uuid.UUID
  fileSize int
}

func (fs *FileSender) SendInitPacket () {
}

func (fs *FileSender) SendPacket () {
}

func (fs *FileSender) CalculateChecksum(reader io.Reader) (uint32, error) {
  hash := crc32.New(crc32.IEEETable)
  _, err := io.Copy(hash, reader)
  if err != nil {
    return 0, err
  }
  checksum := hash.Sum32()
  return uint32(checksum), nil
}

