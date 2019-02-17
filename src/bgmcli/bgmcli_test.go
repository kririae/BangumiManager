package bgmcli

import (
	"fmt"
	"testing"
)

func TestGetInfo(t *testing.T) {
	// fmt.Printf("%+v", GetInfo(103496))
	a := New("kriaeth@yuyuko.cc", "Yomi@0507", "bgm.tv")
	fmt.Println(a.domain)
}
