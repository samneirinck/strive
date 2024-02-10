package main

import (
	"context"
	"database/sql"
	_ "embed"
	"log"
	db "strive/db/sqlc"
	"strive/handler"

	_ "github.com/mattn/go-sqlite3"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

func main() {
	ctx := context.Background()
	database, err := sql.Open("sqlite3", "data/strive.db")
	if err != nil {
		log.Fatal("Unable to connect to database")
	}

	if _, err := database.ExecContext(ctx, "CREATE TABLE activities (id INTEGER PRIMARY KEY);"); err != nil {
		log.Fatal("Failed to create table")
	}

	queries := db.New(database)

	activities, err := queries.ListActivities(ctx)
	if err != nil {
		log.Fatal("Unable to fetch activities")
	}

	log.Print(activities)

	app := echo.New()

	app.HideBanner = true 
	app.Use(middleware.Logger())
	app.Use(middleware.Gzip())

	activitiesHandler := handler.ActivitiesHandler {} 

	app.GET("/activities", activitiesHandler.HandleActivitiesShow)

	app.Start("localhost:8033")
}
