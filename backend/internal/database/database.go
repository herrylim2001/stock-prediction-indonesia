package database

import (
	"log"

	"github.com/herrylim2001/whitelabel-streaming/internal/config"
	"github.com/herrylim2001/whitelabel-streaming/internal/models"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

func Connect(cfg *config.Config) (*gorm.DB, error) {
	var err error

	logLevel := logger.Silent
	if cfg.Environment == "development" {
		logLevel = logger.Info
	}

	DB, err = gorm.Open(postgres.Open(cfg.GetDSN()), &gorm.Config{
		Logger: logger.Default.LogMode(logLevel),
	})
	if err != nil {
		return nil, err
	}

	log.Println("Database connected successfully")
	return DB, nil
}

func Migrate() error {
	log.Println("Running database migrations...")

	err := DB.AutoMigrate(
		&models.Provider{},
		&models.Plan{},
		&models.Client{},
		&models.Host{},
		&models.LiveSession{},
		&models.GiftType{},
		&models.Gift{},
		&models.Payout{},
		&models.ClientGiftMapping{},
	)

	if err != nil {
		return err
	}

	log.Println("Database migrations completed")
	return nil
}
