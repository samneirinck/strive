package handler

import (
	"strive/view/activities"

	"github.com/labstack/echo/v4"
)

type ActivitiesHandler struct {}

func(h ActivitiesHandler) HandleActivitiesShow(c echo.Context) error {
	return render(c, activities.Show())
}
