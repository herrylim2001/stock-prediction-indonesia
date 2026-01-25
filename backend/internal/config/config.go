package config

import (
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

type Config struct {
	// Server
	ServerPort  string
	ServerHost  string
	Environment string

	// Database
	DBType     string // "sqlite" or "postgres"
	SQLitePath string
	DBHost     string
	DBPort     string
	DBUser     string
	DBPassword string
	DBName     string
	DBSSLMode  string

	// JWT
	JWTSecret      string
	JWTExpireHours int

	// CORS
	CORSOrigins []string
}

func Load() *Config {
	// Load .env file if exists
	godotenv.Load()

	expireHours, _ := strconv.Atoi(getEnv("JWT_EXPIRE_HOURS", "24"))

	return &Config{
		// Server
		ServerPort:  getEnv("SERVER_PORT", "8080"),
		ServerHost:  getEnv("SERVER_HOST", "0.0.0.0"),
		Environment: getEnv("ENVIRONMENT", "development"),

		// Database - default to SQLite for easy local development
		DBType:     getEnv("DB_TYPE", "sqlite"),
		SQLitePath: getEnv("SQLITE_PATH", "whitelabel.db"),
		DBHost:     getEnv("DB_HOST", "localhost"),
		DBPort:     getEnv("DB_PORT", "5432"),
		DBUser:     getEnv("DB_USER", "postgres"),
		DBPassword: getEnv("DB_PASSWORD", "postgres"),
		DBName:     getEnv("DB_NAME", "whitelabel_streaming"),
		DBSSLMode:  getEnv("DB_SSL_MODE", "disable"),

		// JWT
		JWTSecret:      getEnv("JWT_SECRET", "your-super-secret-key-change-in-production"),
		JWTExpireHours: expireHours,

		// CORS
		CORSOrigins: []string{
			getEnv("CORS_ORIGIN", "http://localhost:3000"),
		},
	}
}

func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

func (c *Config) GetDSN() string {
	return "host=" + c.DBHost +
		" port=" + c.DBPort +
		" user=" + c.DBUser +
		" password=" + c.DBPassword +
		" dbname=" + c.DBName +
		" sslmode=" + c.DBSSLMode
}
