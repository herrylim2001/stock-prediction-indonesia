package handlers

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/herrylim2001/whitelabel-streaming/internal/models"
	"github.com/herrylim2001/whitelabel-streaming/internal/services"
	"gorm.io/gorm"
)

type HostHandler struct {
	db *gorm.DB
}

func NewHostHandler(db *gorm.DB) *HostHandler {
	return &HostHandler{db: db}
}

type CreateHostRequest struct {
	Email             string  `json:"email" binding:"required,email"`
	Password          string  `json:"password" binding:"required,min=8"`
	DisplayName       string  `json:"display_name" binding:"required"`
	LegalName         string  `json:"legal_name"`
	Bio               string  `json:"bio"`
	PayoutRatePercent float64 `json:"payout_rate_percent"`
}

type UpdateHostRequest struct {
	DisplayName       string  `json:"display_name"`
	LegalName         string  `json:"legal_name"`
	Bio               string  `json:"bio"`
	ProfilePhotoURL   string  `json:"profile_photo_url"`
	PayoutRatePercent float64 `json:"payout_rate_percent"`
	Status            string  `json:"status"`
}

// ListHosts returns all hosts for a client
func (h *HostHandler) ListHosts(c *gin.Context) {
	clientID, _ := c.Get("user_id")

	var hosts []models.Host
	query := h.db.Where("client_id = ?", clientID)

	if status := c.Query("status"); status != "" {
		query = query.Where("status = ?", status)
	}

	if search := c.Query("search"); search != "" {
		query = query.Where("display_name ILIKE ? OR email ILIKE ?", "%"+search+"%", "%"+search+"%")
	}

	if err := query.Find(&hosts).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch hosts"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"hosts": hosts})
}

// GetHost returns a single host
func (h *HostHandler) GetHost(c *gin.Context) {
	clientID, _ := c.Get("user_id")
	hostID := c.Param("id")

	var host models.Host
	if err := h.db.Where("id = ? AND client_id = ?", hostID, clientID).
		Preload("LiveSessions", func(db *gorm.DB) *gorm.DB {
			return db.Order("created_at DESC").Limit(10)
		}).
		First(&host).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Host not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"host": host})
}

// CreateHost creates a new host
func (h *HostHandler) CreateHost(c *gin.Context) {
	clientID, _ := c.Get("user_id")

	var req CreateHostRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Check email uniqueness within client
	var count int64
	h.db.Model(&models.Host{}).Where("email = ? AND client_id = ?", req.Email, clientID).Count(&count)
	if count > 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Email already registered for this client"})
		return
	}

	hashedPassword, err := services.HashPassword(req.Password)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to process password"})
		return
	}

	host := models.Host{
		ClientID:          clientID.(uuid.UUID),
		Email:             req.Email,
		Password:          hashedPassword,
		DisplayName:       req.DisplayName,
		LegalName:         req.LegalName,
		Bio:               req.Bio,
		PayoutRatePercent: req.PayoutRatePercent,
		Status:            models.HostStatusPending,
	}

	if req.PayoutRatePercent == 0 {
		host.PayoutRatePercent = 70 // Default 70%
	}

	if err := h.db.Create(&host).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create host"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"host": host})
}

// UpdateHost updates a host
func (h *HostHandler) UpdateHost(c *gin.Context) {
	clientID, _ := c.Get("user_id")
	hostID := c.Param("id")

	var host models.Host
	if err := h.db.Where("id = ? AND client_id = ?", hostID, clientID).First(&host).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Host not found"})
		return
	}

	var req UpdateHostRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	updates := map[string]interface{}{}
	if req.DisplayName != "" {
		updates["display_name"] = req.DisplayName
	}
	if req.LegalName != "" {
		updates["legal_name"] = req.LegalName
	}
	if req.Bio != "" {
		updates["bio"] = req.Bio
	}
	if req.ProfilePhotoURL != "" {
		updates["profile_photo_url"] = req.ProfilePhotoURL
	}
	if req.PayoutRatePercent > 0 {
		updates["payout_rate_percent"] = req.PayoutRatePercent
	}
	if req.Status != "" {
		updates["status"] = req.Status
	}

	if err := h.db.Model(&host).Updates(updates).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update host"})
		return
	}

	h.db.First(&host, host.ID)
	c.JSON(http.StatusOK, gin.H{"host": host})
}

// DeleteHost soft deletes a host
func (h *HostHandler) DeleteHost(c *gin.Context) {
	clientID, _ := c.Get("user_id")
	hostID := c.Param("id")

	var host models.Host
	if err := h.db.Where("id = ? AND client_id = ?", hostID, clientID).First(&host).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Host not found"})
		return
	}

	if err := h.db.Delete(&host).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete host"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Host deleted successfully"})
}

// ActivateHost activates a pending host
func (h *HostHandler) ActivateHost(c *gin.Context) {
	clientID, _ := c.Get("user_id")
	hostID := c.Param("id")

	var host models.Host
	if err := h.db.Where("id = ? AND client_id = ?", hostID, clientID).First(&host).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Host not found"})
		return
	}

	now := time.Now()
	host.Status = models.HostStatusActive
	host.VerifiedAt = &now

	if err := h.db.Save(&host).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to activate host"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"host": host, "message": "Host activated successfully"})
}

// GetHostProfile returns host's own profile (for host portal)
func (h *HostHandler) GetHostProfile(c *gin.Context) {
	hostID, _ := c.Get("user_id")

	var host models.Host
	if err := h.db.Where("id = ?", hostID).First(&host).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Host not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"host": host})
}

// UpdateHostProfile allows host to update their own profile
func (h *HostHandler) UpdateHostProfile(c *gin.Context) {
	hostID, _ := c.Get("user_id")

	var host models.Host
	if err := h.db.Where("id = ?", hostID).First(&host).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Host not found"})
		return
	}

	var req struct {
		DisplayName     string                 `json:"display_name"`
		Bio             string                 `json:"bio"`
		ProfilePhotoURL string                 `json:"profile_photo_url"`
		SocialLinks     map[string]interface{} `json:"social_links"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	updates := map[string]interface{}{}
	if req.DisplayName != "" {
		updates["display_name"] = req.DisplayName
	}
	if req.Bio != "" {
		updates["bio"] = req.Bio
	}
	if req.ProfilePhotoURL != "" {
		updates["profile_photo_url"] = req.ProfilePhotoURL
	}
	if req.SocialLinks != nil {
		updates["social_links"] = req.SocialLinks
	}

	if err := h.db.Model(&host).Updates(updates).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update profile"})
		return
	}

	h.db.First(&host, host.ID)
	c.JSON(http.StatusOK, gin.H{"host": host})
}

// GetHostEarnings returns host's earnings summary
func (h *HostHandler) GetHostEarnings(c *gin.Context) {
	hostID, _ := c.Get("user_id")

	var host models.Host
	if err := h.db.Where("id = ?", hostID).First(&host).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Host not found"})
		return
	}

	// Get earnings by period
	var todayEarnings, weekEarnings, monthEarnings float64

	now := time.Now()
	startOfDay := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location())
	startOfWeek := startOfDay.AddDate(0, 0, -int(now.Weekday()))
	startOfMonth := time.Date(now.Year(), now.Month(), 1, 0, 0, 0, 0, now.Location())

	h.db.Model(&models.LiveSession{}).
		Where("host_id = ? AND ended_at >= ?", hostID, startOfDay).
		Select("COALESCE(SUM(total_earnings), 0)").
		Scan(&todayEarnings)

	h.db.Model(&models.LiveSession{}).
		Where("host_id = ? AND ended_at >= ?", hostID, startOfWeek).
		Select("COALESCE(SUM(total_earnings), 0)").
		Scan(&weekEarnings)

	h.db.Model(&models.LiveSession{}).
		Where("host_id = ? AND ended_at >= ?", hostID, startOfMonth).
		Select("COALESCE(SUM(total_earnings), 0)").
		Scan(&monthEarnings)

	c.JSON(http.StatusOK, gin.H{
		"available_balance":  host.AvailableBalance,
		"lifetime_earnings":  host.LifetimeEarnings,
		"today_earnings":     todayEarnings,
		"week_earnings":      weekEarnings,
		"month_earnings":     monthEarnings,
	})
}
