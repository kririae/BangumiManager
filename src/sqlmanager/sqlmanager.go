package sqlmanager

import (
	"database/sql"

	"../bgmapi"
)

/*
给某个条目加入新的日期与值
删除某个条目
加入某个条目
*/

// SQLTABLE ...
const SQLTABLE = `
CREATE TABLE IF NOT EXISTS entryinfo (
	id INT UNSIGNED NOT NULL,
	name VARCHAR(100),
	name_cn VARCHAR(100),
	score DOUBLE UNSIGNED NOT NULL,
	score_median DOUBLE UNSIGNED NOT NULL
);
` // ???

// InitDatabase ...
func InitDatabase() {
	db, err := sql.Open("sqlite3", "../../data/data.db")
	if err != nil {
		panic(err)
	}

	db.Exec(SQLTABLE)
}

// AddEntry ...
func AddEntry(value bgmapi.Entry) {
	InitDatabase()

}

// DeleteEntry ...
func DeleteEntry() {

}

// AddInfo ...
func AddInfo() {

}
