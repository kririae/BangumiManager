package utils

import (
	"strconv"
)

// GetMedian ...
func GetMedian(form map[string]int) (ret float64) {
	if len(form) == 0 {
		return float64(0)
	}

	var total int
	for _, value := range form {
		total += value
	}

	var curr float64
	for key, value := range form {
		if curr+float64(value)/float64(total) > 0.5 {
			sub := 0.5 - curr
			v, err := strconv.ParseInt(key, 10, 32)
			HandleError(err)
			return float64(v-1) + sub * float64(value)
		}
		curr += float64(value) / float64(total)
	}
	return float64(0)
}

// HandleError ...
func HandleError(err error) {
	if err != nil {
		panic(err)
	}
}