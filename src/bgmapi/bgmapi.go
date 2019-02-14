package bgmapi

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
)

// URL ... bangumi's api URL
const URL string = "https://api.bgm.tv"

// Entry ...
type Entry struct {
	ID     int    `json:"id"`
	Name   string `json:"name"`
	NameCn string `json:"name_cn"`
	Rating Rating `json:"rating"`
}

// Rating ...
type Rating struct {
	Total int            `json:"total"`
	Count map[string]int `json:"count"`
	Score float64        `json:"score"`
}

// GetInfo ...
func GetInfo(id int) []Entry {
	resp, err := http.Get(fmt.Sprintf("%s/subject/%d", URL, id))
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}

	var ret []Entry
	json.Unmarshal([]byte("["+string(body)+"]"), &ret)
	return ret
}
