package main

import (
	"bytes"
	"io"
	"log"
	"net/http"
	"strings"

	tfutil "github.com/CombatMage/go-tensorflow-utilities"
	"github.com/julienschmidt/httprouter"
)

type imageClassifierAPI struct {
	model *tfutil.Model
}

func main() {
	log.Println("Loading model for image recognition")
	model, err := tfutil.NewModel(
		"/model/tensorflow_inception_graph.pb", "/model/imagenet_comp_graph_label_strings.txt")
	if err != nil {
		log.Fatal(err)
		return
	}

	api := imageClassifierAPI{model: model}

	r := httprouter.New()
	r.POST("/recognize", logRequest(api.classifyUploadedImage))

	log.Println("Starting webserver on port 8080")
	log.Fatal(http.ListenAndServe(":8080", r))
}

type classifyResult struct {
	Filename string         `json:"filename"`
	Labels   []tfutil.Label `json:"labels"`
}

func (classifier imageClassifierAPI) classifyUploadedImage(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	// Read image
	imageFile, header, err := r.FormFile("image")
	// Will contain filename and extension
	imageName := strings.Split(header.Filename, ".")
	if err != nil {
		responseError(w, "Could not read image", http.StatusBadRequest)
		return
	}
	defer imageFile.Close()
	var imageBuffer bytes.Buffer
	// Copy image data to a buffer
	io.Copy(&imageBuffer, imageFile)

	imageType, err := getImageTypeFromName(imageName[1])
	if err != nil {
		responseError(w, "Unsupported image type", http.StatusUnsupportedMediaType)
		return
	}

	log.Println("Try to classify image of type " + imageType)
	result, err := classifier.model.ClassifyImage(&imageBuffer, imageType)
	if err != nil {
		responseError(w, "Could not run inference", http.StatusInternalServerError)
		return
	}

	for _, v := range result {
		log.Println(v.Label)
	}

	responseJSON(w, classifyResult{
		Filename: header.Filename,
		Labels:   result,
	})
}
