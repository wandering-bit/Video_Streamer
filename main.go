package main

import (
	"fmt"
	"net"
	"time"
	"sync"
)

const handShake = "x4tKzQ7GHmY2sC8rJv234FE#FbwdfeeerwePdNaR0uT5asdfasBFdfewrVDFEFEVvasdwZ34fbi3WXqglOMpU9yE1hL6jDnBwFScVkAeHo"
var counter int =0
var userMap map[string]bool
var connectedClients map[string]int64
var mu sync.Mutex

func init() {
	userMap = make(map[string]bool)
	connectedClients = make(map[string]int64)
	fmt.Println("starting checker")
}

func main() {
	go checkConnected() 
	addr := &net.UDPAddr{
		IP:   net.IPv4(0, 0, 0, 0),
		Port: 8000,
		Zone: "",
	}
	conn, err := net.ListenUDP("udp", addr)
	if err != nil {
		return
	}
	defer conn.Close()

	fmt.Println("started udp server")
	for {
		buf := make([]byte, 907)
		_, addr, err := conn.ReadFrom(buf)
		if (err != nil) {
			fmt.Println(err)
			continue
		}
		if (string(buf[:106])==handShake) {
			_, err := conn.WriteTo([]byte("hello"), addr)
			if err != nil {
				println(err)
				continue
			}
			mu.Lock()
				userMap[addr.String()] = true
				connectedClients[addr.String()]=time.Now().Unix()
			mu.Unlock()
			continue
		}
		if (string(buf[:9])=="heartbeat"){
			exists,_ := userMap[addr.String()]
			if exists{
				connectedClients[addr.String()]=time.Now().Unix()
			}
			continue
		}
		for address := range userMap {
			addr,_ := net.ResolveUDPAddr("udp",address)
			_, err := conn.WriteTo(buf, addr)
			if err != nil {
				fmt.Println(err)
			}
		}
	}
}

func checkConnected(){
	for {
		currentTime := time.Now().Unix()
		for addr,time := range connectedClients{
			if currentTime-time > 20 {
				mu.Lock()
				delete(userMap,addr)
				delete(connectedClients,addr)
				mu.Unlock()
			} 
		}
		time.Sleep(10*time.Second)
	}
}
