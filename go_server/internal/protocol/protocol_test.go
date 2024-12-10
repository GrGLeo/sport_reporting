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

  checksum, err := CalculateChecksum(&packet)
	if err != nil {
		t.Fatalf("Failed to calculate checksum: %v", err)
	}

	expectedChecksum := crc32.ChecksumIEEE(packet.Data)
	if checksum != expectedChecksum {
		t.Errorf("Checksum mismatch: got %v, want %v", checksum, expectedChecksum)
	}
}

func TestSendInitPacket(t *testing.T) {
	data := []byte("example file content")
  reader := bytes.NewReader(data)
	userID := uuid.New()
	transactionID := 1234
	fileSize := len(data)

	fileSender := &FileSender{
		File:          reader,
		userID:        userID,
		transactionID: transactionID,
		fileSize:      fileSize,
	}

	expectedChecksum := crc32.ChecksumIEEE(data)

	expectedInitPacket := InitPacket{
		MessageType:    MessageInit,
		TransactionID:  uint16(transactionID),
		FileSize:       uint32(fileSize),
		Checksum:       expectedChecksum,
		UUID:           userID,
	}

	result, err := fileSender.SendInitPacket()

	assert.NoError(t, err, "Expected no error from SendInitPacket")

	buff := bytes.NewReader(result)
	var actualInitPacket InitPacket
	err = binary.Read(buff, binary.BigEndian, &actualInitPacket)

	assert.NoError(t, err, "Failed to decode InitPacket")
	assert.Equal(t, expectedInitPacket, actualInitPacket, "InitPacket mismatch")
}

func TestSendPacket(t *testing.T) {
	payload := []byte("example payload data")
	expectedPayloadSize := uint32(len(payload))
	transactionID := 1234

	fileSender := &FileSender{
		transactionID: transactionID,
	}

	packet := Packet{
		Header: Header{
			MessageType:   MessagePacket,
			TransactionID: uint16(transactionID),
			PayloadSize:   expectedPayloadSize,
		},
		Data: payload,
	}
	expectedChecksum, err := CalculateChecksum(&packet)
	assert.NoError(t, err, "Failed to calculate expected checksum")

	packet.Header.Checksum = expectedChecksum

	expectedBuff := new(bytes.Buffer)
	err = binary.Write(expectedBuff, binary.BigEndian, packet)
	assert.NoError(t, err, "Failed to serialize expected packet")
	expectedBytes := expectedBuff.Bytes()

	resultBytes, err := fileSender.SendPacket(payload)

	assert.NoError(t, err, "Expected no error from SendPacket")
	assert.Equal(t, expectedBytes, resultBytes, "Serialized packet mismatch")

	resultBuff := bytes.NewReader(resultBytes)
	var resultPacket Packet
	err = binary.Read(resultBuff, binary.BigEndian, &resultPacket)
	assert.NoError(t, err, "Failed to decode result packet")
	assert.Equal(t, packet, resultPacket, "Decoded packet mismatch")
}

