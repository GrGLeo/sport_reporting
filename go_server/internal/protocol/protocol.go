package protocol

import (
	"bytes"
	"encoding/binary"
	"errors"
	"hash/crc32"
	"io"
	"net"
	"time"

	"github.com/google/uuid"
)

const (
  ProtocolVersion = 1
  MaxPacketSize = 1024
  ServerAddress = "localhost:8090"
  HeaderSize = 13
  MaxPayloadSize = MaxPacketSize - HeaderSize
  MessageInit = 1
  MessagePacket = 2
  MaxRetries = 5
)

type FileSender struct {
  File io.Reader
  userID uuid.UUID
  fileSize int
  transactionID int
  packetMap map[int]*Packet
}

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
  PacketNumber uint16
  PayloadSize uint32
  Checksum uint32
}


func (fs *FileSender) PrepInitPacket () ([]byte, error) {
  checksum, err := CalculateChecksum(fs.File)
  if err != nil {
    return []byte{}, errors.New("Failed to calculate checksum")
  }

  initPacket := InitPacket{
    MessageType: MessageInit,
    TransactionID: uint16(fs.transactionID),
    FileSize: uint32(fs.fileSize),
    Checksum: checksum,
    UUID: fs.userID,
  }

  buff := new(bytes.Buffer)
  err = binary.Write(buff, binary.BigEndian, initPacket)
  if err != nil {
    return []byte{}, errors.New("Failed to encode initPacket")
  }
    
  initPacketBytes := buff.Bytes()
  return initPacketBytes, nil
}

func (fs *FileSender) PrepPacket (payload []byte, pNumber int) ([]byte, error) {
  packet := Packet{
    Header: Header{
      MessageType: MessagePacket,
      TransactionID: uint16(fs.transactionID),
      PacketNumber: uint16(pNumber),
      PayloadSize: uint32(len(payload)),
    },
    Data: payload,
  }
  checksum, err := CalculateChecksum(&packet)
  if err != nil {
    return []byte{}, errors.New("Failed to calculate checksum")
  }

  packet.Header.Checksum = checksum
  packetBytes, err := packet.Serialize()
  if err != nil {
    return []byte{}, err
  }
  
  return packetBytes, nil
}

func (fs *FileSender) ReSendPacket(packetNumber uint16) ([]byte, error) {
  return []byte{}, nil
}

func (fs *FileSender) SendFile () error {
  con ,err := net.Dial("tcp", ServerAddress)
  if err != nil {
    return err
  }
  defer con.Close()

  initPacket, err := fs.PrepInitPacket()
  
  _, err = con.Write(initPacket)
  con.SetReadDeadline(time.Now().Add(5 * time.Second))
  ack := make([]byte, 1)
  _, err = con.Read(ack)
  // We stop sending if initPacket is not accepted
  if ack[0] != 0x01 {
    return err
  }

  // We start sending the file 1024 byte packet at the time
  buffer := make([]byte, MaxPayloadSize)
  packetNumber := 0 
  for {
    n, err := fs.File.Read(buffer)
    if err != nil {
      if err == io.EOF {
        break
      }
      return err
    }
    chunk := buffer[:n]
    packetNumber++
    fs.PrepPacket(chunk, packetNumber)
    _, err = con.Write(initPacket)
  }


  for try := 0; try < MaxRetries; try++ {
    ack = make([]byte, 516)
    n, _ := con.Read(ack)
    if ack[0] == 0x01 {
      break
    }
    
    if n < 2 {
      errors.New("Invalid ack format")
      continue
    }
    numMissing := int(ack[1])
    if n < 2 * numMissing + 2 {
      errors.New("Invalid ack format")
      continue
    }

    for i := 0; i < numMissing; i++ {
      start := 2 + i*2
      packetMissing := binary.BigEndian.Uint16(ack[start:start+2])
      fs.ReSendPacket(packetMissing)
    }
    
    time.Sleep(100 * time.Millisecond)
  }

  return nil
}

func CalculateChecksum(reader io.Reader) (uint32, error) {
  hash := crc32.New(crc32.IEEETable)
  _, err := io.Copy(hash, reader)
  if err != nil {
    return 0, err
  }
  checksum := hash.Sum32()
  return uint32(checksum), nil
}

