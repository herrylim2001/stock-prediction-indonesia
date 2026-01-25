package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/herrylim2001/whitelabel-streaming/internal/services"
)

type AuthHandler struct {
	authService *services.AuthService
}

func NewAuthHandler(authService *services.AuthService) *AuthHandler {
	return &AuthHandler{authService: authService}
}

// Login handles authentication for all user types
// @Summary Login
// @Description Authenticate user and get JWT token
// @Tags Auth
// @Accept json
// @Produce json
// @Param request body services.LoginRequest true "Login credentials"
// @Success 200 {object} services.LoginResponse
// @Failure 400 {object} map[string]string
// @Failure 401 {object} map[string]string
// @Router /api/v1/auth/login [post]
func (h *AuthHandler) Login(c *gin.Context) {
	var req services.LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	response, err := h.authService.Login(req)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, response)
}

// RegisterProvider creates a new provider account
// @Summary Register Provider
// @Description Create a new provider (super admin) account
// @Tags Auth
// @Accept json
// @Produce json
// @Param request body services.RegisterProviderRequest true "Provider registration"
// @Success 201 {object} models.Provider
// @Failure 400 {object} map[string]string
// @Router /api/v1/auth/register/provider [post]
func (h *AuthHandler) RegisterProvider(c *gin.Context) {
	var req services.RegisterProviderRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	provider, err := h.authService.RegisterProvider(req)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"message": "Provider registered successfully",
		"provider": map[string]interface{}{
			"id":           provider.ID,
			"name":         provider.Name,
			"email":        provider.Email,
			"company_name": provider.CompanyName,
		},
	})
}

// GetMe returns the current user's information
// @Summary Get current user
// @Description Get the authenticated user's profile
// @Tags Auth
// @Produce json
// @Security BearerAuth
// @Success 200 {object} map[string]interface{}
// @Failure 401 {object} map[string]string
// @Router /api/v1/auth/me [get]
func (h *AuthHandler) GetMe(c *gin.Context) {
	userID, _ := c.Get("user_id")
	email, _ := c.Get("email")
	role, _ := c.Get("role")

	c.JSON(http.StatusOK, gin.H{
		"user_id": userID,
		"email":   email,
		"role":    role,
	})
}
