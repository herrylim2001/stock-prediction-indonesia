package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/herrylim2001/whitelabel-streaming/internal/models"
	"github.com/herrylim2001/whitelabel-streaming/internal/services"
	"gorm.io/gorm"
)

type ClientHandler struct {
	db *gorm.DB
}

func NewClientHandler(db *gorm.DB) *ClientHandler {
	return &ClientHandler{db: db}
}

type CreateClientRequest struct {
	CompanyName         string  `json:"company_name" binding:"required"`
	ContactName         string  `json:"contact_name" binding:"required"`
	ContactEmail        string  `json:"contact_email" binding:"required,email"`
	ContactPhone        string  `json:"contact_phone"`
	Password            string  `json:"password" binding:"required,min=8"`
	PlanID              string  `json:"plan_id"`
	RevenueSharePercent float64 `json:"revenue_share_percent"`
}

type UpdateClientRequest struct {
	CompanyName         string  `json:"company_name"`
	ContactName         string  `json:"contact_name"`
	ContactPhone        string  `json:"contact_phone"`
	PlanID              string  `json:"plan_id"`
	RevenueSharePercent float64 `json:"revenue_share_percent"`
	MinHostPayout       float64 `json:"min_host_payout"`
	Status              string  `json:"status"`
}

// ListClients returns all clients for a provider
func (h *ClientHandler) ListClients(c *gin.Context) {
	providerID, _ := c.Get("user_id")

	var clients []models.Client
	query := h.db.Where("provider_id = ?", providerID).Preload("Plan")

	// Filter by status
	if status := c.Query("status"); status != "" {
		query = query.Where("status = ?", status)
	}

	// Search
	if search := c.Query("search"); search != "" {
		query = query.Where("company_name ILIKE ? OR contact_email ILIKE ?", "%"+search+"%", "%"+search+"%")
	}

	if err := query.Find(&clients).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch clients"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"clients": clients})
}

// GetClient returns a single client
func (h *ClientHandler) GetClient(c *gin.Context) {
	providerID, _ := c.Get("user_id")
	clientID := c.Param("id")

	var client models.Client
	if err := h.db.Where("id = ? AND provider_id = ?", clientID, providerID).
		Preload("Plan").
		Preload("Hosts").
		First(&client).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Client not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"client": client})
}

// CreateClient creates a new client
func (h *ClientHandler) CreateClient(c *gin.Context) {
	providerID, _ := c.Get("user_id")

	var req CreateClientRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Check email uniqueness
	var count int64
	h.db.Model(&models.Client{}).Where("contact_email = ?", req.ContactEmail).Count(&count)
	if count > 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Email already registered"})
		return
	}

	// Hash password
	hashedPassword, err := services.HashPassword(req.Password)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to process password"})
		return
	}

	client := models.Client{
		ProviderID:          providerID.(uuid.UUID),
		CompanyName:         req.CompanyName,
		ContactName:         req.ContactName,
		ContactEmail:        req.ContactEmail,
		ContactPhone:        req.ContactPhone,
		Password:            hashedPassword,
		RevenueSharePercent: req.RevenueSharePercent,
		Status:              models.ClientStatusPending,
	}

	if req.PlanID != "" {
		planID, _ := uuid.Parse(req.PlanID)
		client.PlanID = planID
	}

	if req.RevenueSharePercent == 0 {
		client.RevenueSharePercent = 70 // Default 70% to client
	}

	if err := h.db.Create(&client).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create client"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"client": client})
}

// UpdateClient updates a client
func (h *ClientHandler) UpdateClient(c *gin.Context) {
	providerID, _ := c.Get("user_id")
	clientID := c.Param("id")

	var client models.Client
	if err := h.db.Where("id = ? AND provider_id = ?", clientID, providerID).First(&client).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Client not found"})
		return
	}

	var req UpdateClientRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	updates := map[string]interface{}{}
	if req.CompanyName != "" {
		updates["company_name"] = req.CompanyName
	}
	if req.ContactName != "" {
		updates["contact_name"] = req.ContactName
	}
	if req.ContactPhone != "" {
		updates["contact_phone"] = req.ContactPhone
	}
	if req.PlanID != "" {
		planID, _ := uuid.Parse(req.PlanID)
		updates["plan_id"] = planID
	}
	if req.RevenueSharePercent > 0 {
		updates["revenue_share_percent"] = req.RevenueSharePercent
	}
	if req.MinHostPayout > 0 {
		updates["min_host_payout"] = req.MinHostPayout
	}
	if req.Status != "" {
		updates["status"] = req.Status
	}

	if err := h.db.Model(&client).Updates(updates).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update client"})
		return
	}

	h.db.First(&client, client.ID)
	c.JSON(http.StatusOK, gin.H{"client": client})
}

// DeleteClient soft deletes a client
func (h *ClientHandler) DeleteClient(c *gin.Context) {
	providerID, _ := c.Get("user_id")
	clientID := c.Param("id")

	var client models.Client
	if err := h.db.Where("id = ? AND provider_id = ?", clientID, providerID).First(&client).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Client not found"})
		return
	}

	if err := h.db.Delete(&client).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete client"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Client deleted successfully"})
}

// ActivateClient activates a pending client
func (h *ClientHandler) ActivateClient(c *gin.Context) {
	providerID, _ := c.Get("user_id")
	clientID := c.Param("id")

	var client models.Client
	if err := h.db.Where("id = ? AND provider_id = ?", clientID, providerID).First(&client).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Client not found"})
		return
	}

	client.Status = models.ClientStatusActive
	if err := h.db.Save(&client).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to activate client"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"client": client, "message": "Client activated successfully"})
}

// SuspendClient suspends a client
func (h *ClientHandler) SuspendClient(c *gin.Context) {
	providerID, _ := c.Get("user_id")
	clientID := c.Param("id")

	var client models.Client
	if err := h.db.Where("id = ? AND provider_id = ?", clientID, providerID).First(&client).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Client not found"})
		return
	}

	client.Status = models.ClientStatusSuspended
	if err := h.db.Save(&client).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to suspend client"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"client": client, "message": "Client suspended successfully"})
}
