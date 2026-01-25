package services

import (
	"errors"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"github.com/herrylim2001/whitelabel-streaming/internal/config"
	"github.com/herrylim2001/whitelabel-streaming/internal/middleware"
	"github.com/herrylim2001/whitelabel-streaming/internal/models"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

type AuthService struct {
	db  *gorm.DB
	cfg *config.Config
}

func NewAuthService(db *gorm.DB, cfg *config.Config) *AuthService {
	return &AuthService{db: db, cfg: cfg}
}

type LoginRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required"`
	Role     string `json:"role" binding:"required,oneof=provider client host"`
}

type LoginResponse struct {
	Token     string                 `json:"token"`
	ExpiresAt time.Time              `json:"expires_at"`
	User      map[string]interface{} `json:"user"`
}

type RegisterProviderRequest struct {
	Name        string `json:"name" binding:"required"`
	Email       string `json:"email" binding:"required,email"`
	Password    string `json:"password" binding:"required,min=8"`
	Phone       string `json:"phone"`
	CompanyName string `json:"company_name"`
}

func (s *AuthService) Login(req LoginRequest) (*LoginResponse, error) {
	var userID uuid.UUID
	var email, hashedPassword string
	var userData map[string]interface{}

	switch req.Role {
	case "provider":
		var provider models.Provider
		if err := s.db.Where("email = ?", req.Email).First(&provider).Error; err != nil {
			return nil, errors.New("invalid credentials")
		}
		userID = provider.ID
		email = provider.Email
		hashedPassword = provider.Password
		userData = map[string]interface{}{
			"id":           provider.ID,
			"name":         provider.Name,
			"email":        provider.Email,
			"company_name": provider.CompanyName,
			"role":         "provider",
		}

	case "client":
		var client models.Client
		if err := s.db.Where("contact_email = ?", req.Email).First(&client).Error; err != nil {
			return nil, errors.New("invalid credentials")
		}
		if client.Status != models.ClientStatusActive {
			return nil, errors.New("account is not active")
		}
		userID = client.ID
		email = client.ContactEmail
		hashedPassword = client.Password
		userData = map[string]interface{}{
			"id":           client.ID,
			"company_name": client.CompanyName,
			"email":        client.ContactEmail,
			"role":         "client",
		}

	case "host":
		var host models.Host
		if err := s.db.Where("email = ?", req.Email).First(&host).Error; err != nil {
			return nil, errors.New("invalid credentials")
		}
		if host.Status != models.HostStatusActive {
			return nil, errors.New("account is not active")
		}
		userID = host.ID
		email = host.Email
		hashedPassword = host.Password
		userData = map[string]interface{}{
			"id":           host.ID,
			"display_name": host.DisplayName,
			"email":        host.Email,
			"role":         "host",
		}

	default:
		return nil, errors.New("invalid role")
	}

	// Verify password
	if err := bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(req.Password)); err != nil {
		return nil, errors.New("invalid credentials")
	}

	// Generate JWT
	expiresAt := time.Now().Add(time.Duration(s.cfg.JWTExpireHours) * time.Hour)
	claims := &middleware.Claims{
		UserID: userID,
		Email:  email,
		Role:   middleware.UserRole(req.Role),
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(expiresAt),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte(s.cfg.JWTSecret))
	if err != nil {
		return nil, err
	}

	return &LoginResponse{
		Token:     tokenString,
		ExpiresAt: expiresAt,
		User:      userData,
	}, nil
}

func (s *AuthService) RegisterProvider(req RegisterProviderRequest) (*models.Provider, error) {
	// Check if email exists
	var count int64
	s.db.Model(&models.Provider{}).Where("email = ?", req.Email).Count(&count)
	if count > 0 {
		return nil, errors.New("email already registered")
	}

	// Hash password
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}

	provider := &models.Provider{
		Name:        req.Name,
		Email:       req.Email,
		Password:    string(hashedPassword),
		Phone:       req.Phone,
		CompanyName: req.CompanyName,
	}

	if err := s.db.Create(provider).Error; err != nil {
		return nil, err
	}

	return provider, nil
}

func HashPassword(password string) (string, error) {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(hashedPassword), nil
}
