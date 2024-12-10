package protocol

import (
	"hash/crc32"
	"testing"
)

func TestCalculateChecksum(t *testing.T) {
  packet := Packet{
    Header: Header{},
    Data: []byte("example data"),
  }

  FileSender := FileSender{}

  checksum, err := FileSender.CalculateChecksum(&packet)
	if err != nil {
		t.Fatalf("Failed to calculate checksum: %v", err)
	}

	expectedChecksum := crc32.ChecksumIEEE(packet.Data)
	if checksum != expectedChecksum {
		t.Errorf("Checksum mismatch: got %v, want %v", checksum, expectedChecksum)
	}

}
