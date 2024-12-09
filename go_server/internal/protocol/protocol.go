package protocol

import "github.com/google/uuid"

type SpecialHeader struct {
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
