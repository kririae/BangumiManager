package bgmcli

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"strings"

	"../utils"
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
	utils.HandleError(err)
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	utils.HandleError(err)

	var ret []Entry
	json.Unmarshal([]byte("["+string(body)+"]"), &ret)
	return ret
}

/*
BgmSession ...
*/
type BgmSession struct {
	email    string
	password string
	userID   int
	domain   string
	_login   bool
	_client  http.Client
}

func login() {

}

// New ...
func New(_email, _password, _domain string) (ret *BgmSession) {
	if !strings.HasPrefix(_domain, "https://") && !strings.HasPrefix(_domain, "http://") {
		_domain = "https://" + _domain
	}

	jar, err := cookiejar.New(nil)
	utils.HandleError(err)

	ret = &BgmSession{
		email:    _email,
		password: _password,
		domain:   _domain,
		_client: http.Client{
			Jar: jar,
		},
	}

	resp, err := ret._client.PostForm(_domain+"/FollowTheRabbit",
		url.Values{
			"formhash":    {""},
			"email":       {_email},
			"password":    {_password},
			"loginsummit": {"登录"},
		})
	utils.HandleError(err)
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)

	utils.HandleError(err)
	fmt.Println(string(body))
	// 怎么扒验证码模块啊...bangumi的openapi貌似不能操作游戏啊呜呜呜
	return ret
}
