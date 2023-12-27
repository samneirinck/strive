package main

import (
	"fmt"
	"net/http"

	"github.com/a-h/templ"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"

	"strive/views"
)

func main() {
	r := chi.NewRouter()
	r.Use(middleware.Logger)

	r.Handle("/", templ.Handler(views.Index()))
	fmt.Println("Listening on 8033...")

	http.ListenAndServe(":8033", r)
}
