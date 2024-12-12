package protocol

import (
	"bytes"
	"encoding/binary"
	"hash/crc32"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

func TestCalculateChecksum(t *testing.T) {
  packet := Packet{
    Header: Header{},
    Data: []byte("example data"),
  }

  data := bytes.NewBuffer(packet.Data)
  checksum, err := CalculateChecksum(*data)
	if err != nil {
		t.Fatalf("Failed to calculate checksum: %v", err)
	}

	expectedChecksum := crc32.ChecksumIEEE(packet.Data)
	if checksum != expectedChecksum {
		t.Errorf("Checksum mismatch: got %v, want %v", checksum, expectedChecksum)
	}
}

func TestPrepInitPacket(t *testing.T) {
	data := []byte("example file content")
  reader := bytes.NewBuffer(data)
	userID := uuid.New()
	transactionID := 1234
	fileSize := len(data)

	fileSender := &FileSender{
		File:          *reader,
		UserID:        userID,
		TransactionID: transactionID,
		FileSize:      fileSize,
	}

	expectedChecksum := crc32.ChecksumIEEE(data)

	expectedInitPacket := InitPacket{
		MessageType:    MessageInit,
		TransactionID:  uint16(transactionID),
		FileSize:       uint32(fileSize),
		Checksum:       expectedChecksum,
		UUID:           userID,
	}

	result, err := fileSender.PrepInitPacket()

	assert.NoError(t, err, "Expected no error from PrepInitPacket")

	buff := bytes.NewReader(result)
	var actualInitPacket InitPacket
	err = binary.Read(buff, binary.BigEndian, &actualInitPacket)

	assert.NoError(t, err, "Failed to decode InitPacket")
	assert.Equal(t, expectedInitPacket, actualInitPacket, "InitPacket mismatch")
}


func TestPacketSerialize(t *testing.T) {
	header := Header{
		MessageType:   1,
		TransactionID: 12345,
		PayloadSize:      256,
		Checksum:      987654321,
	}
	data := []byte{1, 2, 3, 4, 5}

	packet := Packet{
		Header: header,
		Data:   data,
	}

	serializedBytes, err := packet.Serialize()
	if err != nil {
		t.Fatalf("Serialize() returned an error: %v", err)
	}

	expectedBuffer := new(bytes.Buffer)

	err = binary.Write(expectedBuffer, binary.BigEndian, header)
	if err != nil {
		t.Fatalf("Failed to manually serialize header: %v", err)
	}

	err = binary.Write(expectedBuffer, binary.BigEndian, data)
	if err != nil {
		t.Fatalf("Failed to manually serialize data: %v", err)
	}

	expectedBytes := expectedBuffer.Bytes()

	if !bytes.Equal(serializedBytes, expectedBytes) {
		t.Errorf("Serialized output does not match expected output.\nGot: %v\nExpected: %v", serializedBytes, expectedBytes)
	}
}

func TestPrepPacket(t *testing.T) {
	payload := []byte("example payload data")
	expectedPayloadSize := uint32(len(payload))
	transactionID := 1234

	_ = &FileSender{
		TransactionID: transactionID,
	}

	packet := Packet{
		Header: Header{
			MessageType:   MessagePacket,
			TransactionID: uint16(transactionID),
			PayloadSize:   expectedPayloadSize,
		},
		Data: payload,
	}
  data := bytes.NewBuffer(packet.Data)
	expectedChecksum, err := CalculateChecksum(*data)
	assert.NoError(t, err, "Failed to calculate expected checksum")

	packet.Header.Checksum = expectedChecksum

	// expectedBuff := new(bytes.Buffer)
	// err = binary.Write(expectedBuff, binary.BigEndian, packet)
	// assert.NoError(t, err, "Failed to serialize expected packet")
	// expectedBytes := expectedBuff.Bytes()

	// resultBytes, err := fileSender.PrepPacket(payload)

	// assert.NoError(t, err, "Expected no error from PrepPacket")
	// assert.Equal(t, expectedBytes, resultBytes, "Serialized packet mismatch")

	// resultBuff := bytes.NewReader(resultBytes)
	// var resultPacket Packet
	// err = binary.Read(resultBuff, binary.BigEndian, &resultPacket)
	// assert.NoError(t, err, "Failed to decode result packet")
	// assert.Equal(t, packet, resultPacket, "Decoded packet mismatch")
}

