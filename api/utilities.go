package main

import (
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"strings"
	"time"

	tfutil "github.com/CombatMage/go-tensorflow-utilities"
	"github.com/julienschmidt/httprouter"
)

func responseError(w http.ResponseWriter, message string, code int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(map[string]string{"error": message})
}

func responseJSON(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}

func logRequest(fn httprouter.Handle) httprouter.Handle {
	return func(w http.ResponseWriter, r *http.Request, params httprouter.Params) {
		timestamp := time.Now()
		log.Printf("%s - %s\n", timestamp.Format("Mon Jan 2 15:04:05 2006"), r.URL.Path)
		fn(w, r, params)
	}
}

func getImageTypeFromName(imageName string) (tfutil.ImageType, error) {
	lowercase := strings.ToLower(imageName)
	if strings.HasSuffix(lowercase, "png") {
		return tfutil.PNG, nil
	} else if strings.HasSuffix(lowercase, "jpg") || strings.HasSuffix(lowercase, "jpeg") {
		return tfutil.JPG, nil
	} else {
		return "", errors.New("Invalid image type: " + imageName)
	}
}
