package protocol

import "io"

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


