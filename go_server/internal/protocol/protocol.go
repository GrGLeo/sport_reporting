package protocol

import (
	"bytes"
	"encoding/binary"
	"errors"
	"fmt"
	"hash/crc32"
	"io"
	"net"
	"os"
	"time"

	"github.com/google/uuid"
)

const (
  ProtocolVersion = 1
  MaxPacketSize = 1024
  ServerAddress = "udp_server:12345"
  HeaderSize = 13
  MaxPayloadSize = MaxPacketSize - HeaderSize
  MessageInit = 1
  MessagePacket = 2
  MessageEnd = 3
  MaxRetries = 5
)

type FileSender struct {
  File bytes.Buffer
  UserID uuid.UUID
  FileSize int
  TransactionID int
  PacketMap map[int][]byte
}

type InitPacket struct {
  MessageType uint8
  TransactionID uint16
  FileSize uint32
  Checksum uint32
  UUID uuid.UUID
}

type EndPacket struct {
  MessageType uint8
  TransactionID uint16
  PacketNumberSend uint16
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
    TransactionID: uint16(fs.TransactionID),
    FileSize: uint32(fs.FileSize),
    Checksum: checksum,
    UUID: fs.UserID,
  }

  buff := new(bytes.Buffer)
  err = binary.Write(buff, binary.BigEndian, initPacket)
  if err != nil {
    return []byte{}, errors.New("Failed to encode initPacket")
  }
    
  initPacketBytes := buff.Bytes()
  return initPacketBytes, nil
}

func (fs *FileSender) PrepEndPacket(pNumber int) ([]byte, error) {
  endPacket := EndPacket{
    MessageType: MessageEnd,
    TransactionID: uint16(fs.TransactionID),
    PacketNumberSend: uint16(pNumber),
  }

  buff := new(bytes.Buffer)
  err := binary.Write(buff, binary.BigEndian, endPacket)
  if err != nil {
    return []byte{}, errors.New("Failed to encode initPacket")
  }

  endPacketBytes := buff.Bytes()
  return endPacketBytes, nil
}


func (fs *FileSender) PrepPacket (payload []byte, pNumber int) ([]byte, error) {
  packet := Packet{
    Header: Header{
      MessageType: MessagePacket,
      TransactionID: uint16(fs.TransactionID),
      PacketNumber: uint16(pNumber),
      PayloadSize: uint32(len(payload)),
    },
    Data: payload,
  }
  data := bytes.NewBuffer(packet.Data)
  checksum, err := CalculateChecksum(*data)
  if err != nil {
    return []byte{}, errors.New("Failed to calculate checksum")
  }

  packet.Header.Checksum = checksum
  packetBytes, err := packet.Serialize()
  if err != nil {
    return []byte{}, err
  }
  
  fs.PacketMap[pNumber] = packetBytes
  return packetBytes, nil
}

func (fs *FileSender) ReSendPacket(packetNumber uint16) ([]byte, error) {
  return []byte{}, nil
}

func (fs *FileSender) SendFile () error {
  con ,err := net.Dial("udp", ServerAddress)
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
  fmt.Println("receive ok from server")

  // We start sending the file 1024 byte packet at the time
  buffer := make([]byte, MaxPayloadSize)
  packetNumber := 0 
  for {
    n, err := fs.File.Read(buffer)
    fmt.Println(fmt.Sprintf("Bytes read: %d, Error: %v\n", n, err))
    if err != nil {
      if err == io.EOF {
        endPacket, _ := fs.PrepEndPacket(packetNumber)
        _, err = con.Write(endPacket)
        break
      }
      return err
    }
    chunk := buffer[:n]
    // Update packet number
    packetNumber++
    packet, err := fs.PrepPacket(chunk, packetNumber)
    if err != nil {
      fmt.Println(err)
    }
    if packetNumber == 69 {
      continue
    }
    _, err = con.Write(packet)
    fmt.Println("send!")
  }

  for try := 0; try < MaxRetries; try++ {
    ack = make([]byte, 516)
    n, _ := con.Read(ack)
    fmt.Println(n)
    if ack[0] == 0x01 {
      break
    }
    
    if n < 2 {
      // errors.New("Invalid ack format")
      continue
    }
    var numMissing uint16
    _ = binary.Read(bytes.NewReader(ack[1:3]), binary.BigEndian, &numMissing)
    num := int(numMissing)
    fmt.Println(numMissing)
    if n < 2 * num + 2 {
      // errors.New("Invalid ack format")
      continue
    }

    for i := 0; i < num; i++ {
      start := 3 + i*2
      packetMissing := binary.BigEndian.Uint16(ack[start:start+2])
      fmt.Println(packetMissing)
      fs.ReSendPacket(packetMissing)
    }
    
    time.Sleep(100 * time.Millisecond)
  }

  return nil
}

func CalculateChecksum(reader bytes.Buffer) (uint32, error) {
  hash := crc32.New(crc32.IEEETable)
  _, err := io.Copy(hash, &reader)
  if err != nil {
    return 0, err
  }
  checksum := hash.Sum32()
  return uint32(checksum), nil
}

func resetFilePointer(file *os.File) error {
    _, err := file.Seek(0, io.SeekStart)
    return err
}

