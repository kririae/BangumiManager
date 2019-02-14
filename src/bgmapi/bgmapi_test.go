package bgmapi

import (
	"fmt"
	"testing"
)

func TestGetInfo(t *testing.T) {
	fmt.Printf("%+v", GetInfo(103496))
}
