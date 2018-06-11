package main

import (
	"crypto/md5"
	"fmt"
	"html/template"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"
)

type webPage struct {
	templates *template.Template
}

func main() {
	log.Println("Loading templates")
	wp := webPage{}
	wp.templates = template.Must(
		template.ParseFiles(
			"./template/upload.html",
		),
	)

	http.HandleFunc("/", logRequest(wp.showUploadForm))
	http.HandleFunc("/upload", logRequest(upload))

	log.Println("Starting webserver on port 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func (webPage webPage) showUploadForm(w http.ResponseWriter, r *http.Request) {
	err := webPage.templates.ExecuteTemplate(w, "upload.html", nil)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func upload(w http.ResponseWriter, r *http.Request) {
	fmt.Println("method:", r.Method)
	if r.Method == "GET" {
		crutime := time.Now().Unix()
		h := md5.New()
		io.WriteString(h, strconv.FormatInt(crutime, 10))
		token := fmt.Sprintf("%x", h.Sum(nil))

		t, _ := template.ParseFiles("upload.gtpl")
		t.Execute(w, token)
	} else {
		r.ParseMultipartForm(32 << 20)
		file, handler, err := r.FormFile("image")
		if err != nil {
			fmt.Println(err)
			return
		}
		defer file.Close()
		fmt.Fprintf(w, "%v", handler.Header)
		f, err := os.OpenFile("./test/"+handler.Filename, os.O_WRONLY|os.O_CREATE, 0666)
		if err != nil {
			fmt.Println(err)
			return
		}
		defer f.Close()
		io.Copy(f, file)
	}
}

func logRequest(fn http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		timestamp := time.Now()
		fmt.Printf("%s - %s\n", timestamp.Format("Mon Jan 2 15:04:05 2006"), r.URL.Path)
		fn(w, r)
	}
}
