from pydantic import BaseModel, Field


class CurrentWeatherDTO(BaseModel):
    temperature: float = Field(..., description="Температура в градусах Цельсия")
    windspeed: float | None = Field(None, description="Скорость ветра")
    weathercode: int | None = Field(None, description="Код погодного состояния")


class WeatherDTO(BaseModel):
    current_weather: CurrentWeatherDTO
