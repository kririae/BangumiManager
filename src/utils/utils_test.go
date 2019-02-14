package utils

import (
	"fmt"
	"testing"
)

func TestGetMedian(t *testing.T) {
	a := map[string]int{"1": 0, "2": 1, "3": 2, "4": 1}
	fmt.Println(GetMedian(a))
}
