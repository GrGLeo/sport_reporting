package protocol

import (
	"bytes"
	"encoding/binary"
	"errors"
	"io"
)

type Packet struct {
  Header Header
  Data []byte
  cursor int
}

func (p *Packet) Read (h []byte) (int, error) {
  if p.cursor >= len(p.Data) {
    return 0, io.EOF
  }

  n := copy(h, p.Data[p.cursor:])
  p.cursor += n
  return n, nil
}

func (p *Packet) Serialize() ([]byte, error) {
  buff := new(bytes.Buffer)
	err := binary.Write(buff, binary.BigEndian, p.Header)
	if err != nil {
		return nil, errors.New("failed to serialize packet")
	}
  
  dataLength := uint32(len(p.Data))
  err = binary.Write(buff, binary.BigEndian, dataLength)
	if err != nil {
		return nil, errors.New("failed to serialize packet")
	}
  
  _, err = buff.Write(p.Data)
	if err != nil {
		return nil, errors.New("failed to serialize packet")
	}

	return buff.Bytes(), nil
}
