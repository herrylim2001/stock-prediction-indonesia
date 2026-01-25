package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/herrylim2001/whitelabel-streaming/internal/models"
	"gorm.io/gorm"
)

type GiftHandler struct {
	db *gorm.DB
}

func NewGiftHandler(db *gorm.DB) *GiftHandler {
	return &GiftHandler{db: db}
}

type CreateGiftTypeRequest struct {
	Name         string  `json:"name" binding:"required"`
	IconURL      string  `json:"icon_url"`
	AnimationURL string  `json:"animation_url"`
	Price        float64 `json:"price" binding:"required,gt=0"`
	SortOrder    int     `json:"sort_order"`
}

// Provider: List all gift types
func (h *GiftHandler) ListGiftTypes(c *gin.Context) {
	providerID, _ := c.Get("user_id")

	var gifts []models.GiftType
	h.db.Where("provider_id = ?", providerID).Order("sort_order ASC").Find(&gifts)

	c.JSON(http.StatusOK, gin.H{"gift_types": gifts})
}

// Provider: Create gift type
func (h *GiftHandler) CreateGiftType(c *gin.Context) {
	providerID, _ := c.Get("user_id")

	var req CreateGiftTypeRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	gift := models.GiftType{
		ProviderID:   providerID.(uuid.UUID),
		Name:         req.Name,
		IconURL:      req.IconURL,
		AnimationURL: req.AnimationURL,
		Price:        req.Price,
		SortOrder:    req.SortOrder,
		IsActive:     true,
	}

	if err := h.db.Create(&gift).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create gift type"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"gift_type": gift})
}

// Provider: Update gift type
func (h *GiftHandler) UpdateGiftType(c *gin.Context) {
	providerID, _ := c.Get("user_id")
	giftID := c.Param("id")

	var gift models.GiftType
	if err := h.db.Where("id = ? AND provider_id = ?", giftID, providerID).First(&gift).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Gift type not found"})
		return
	}

	var req struct {
		Name         string   `json:"name"`
		IconURL      string   `json:"icon_url"`
		AnimationURL string   `json:"animation_url"`
		Price        *float64 `json:"price"`
		SortOrder    *int     `json:"sort_order"`
		IsActive     *bool    `json:"is_active"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	updates := map[string]interface{}{}
	if req.Name != "" {
		updates["name"] = req.Name
	}
	if req.IconURL != "" {
		updates["icon_url"] = req.IconURL
	}
	if req.AnimationURL != "" {
		updates["animation_url"] = req.AnimationURL
	}
	if req.Price != nil {
		updates["price"] = *req.Price
	}
	if req.SortOrder != nil {
		updates["sort_order"] = *req.SortOrder
	}
	if req.IsActive != nil {
		updates["is_active"] = *req.IsActive
	}

	if err := h.db.Model(&gift).Updates(updates).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update gift type"})
		return
	}

	h.db.First(&gift, gift.ID)
	c.JSON(http.StatusOK, gin.H{"gift_type": gift})
}

// Provider: Delete gift type
func (h *GiftHandler) DeleteGiftType(c *gin.Context) {
	providerID, _ := c.Get("user_id")
	giftID := c.Param("id")

	var gift models.GiftType
	if err := h.db.Where("id = ? AND provider_id = ?", giftID, providerID).First(&gift).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Gift type not found"})
		return
	}

	if err := h.db.Delete(&gift).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete gift type"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Gift type deleted"})
}

// Send a gift during a live session (called by viewer app)
func (h *GiftHandler) SendGift(c *gin.Context) {
	sessionID := c.Param("session_id")

	var req struct {
		GiftTypeID string `json:"gift_type_id" binding:"required"`
		ViewerID   string `json:"viewer_id" binding:"required"`
		Quantity   int    `json:"quantity" binding:"required,gt=0"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get session
	var session models.LiveSession
	if err := h.db.Where("id = ? AND status = ?", sessionID, models.SessionStatusLive).
		Preload("Host.Client").First(&session).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found or not live"})
		return
	}

	// Get gift type
	var giftType models.GiftType
	if err := h.db.Where("id = ? AND is_active = ?", req.GiftTypeID, true).First(&giftType).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Gift type not found"})
		return
	}

	// Calculate revenue split
	totalValue := giftType.Price * float64(req.Quantity)
	providerFee := totalValue * 0.20 // 20% platform fee

	clientRevenue := totalValue - providerFee
	clientShare := clientRevenue * (1 - session.Host.Client.RevenueSharePercent/100)
	hostEarning := clientRevenue * (session.Host.PayoutRatePercent / 100)

	giftTypeID, _ := uuid.Parse(req.GiftTypeID)
	gift := models.Gift{
		SessionID:   session.ID,
		GiftTypeID:  giftTypeID,
		ViewerID:    req.ViewerID,
		Quantity:    req.Quantity,
		UnitPrice:   giftType.Price,
		TotalValue:  totalValue,
		ProviderFee: providerFee,
		ClientShare: clientShare,
		HostEarning: hostEarning,
	}

	tx := h.db.Begin()

	if err := tx.Create(&gift).Error; err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to record gift"})
		return
	}

	// Update session stats
	tx.Model(&session).Updates(map[string]interface{}{
		"total_gifts":      gorm.Expr("total_gifts + ?", req.Quantity),
		"total_gift_value": gorm.Expr("total_gift_value + ?", totalValue),
		"total_earnings":   gorm.Expr("total_earnings + ?", hostEarning),
	})

	tx.Commit()

	c.JSON(http.StatusCreated, gin.H{
		"gift": gift,
		"gift_type": giftType,
	})
}

// Client: Get available gift types
func (h *GiftHandler) GetClientGiftTypes(c *gin.Context) {
	clientID, _ := c.Get("user_id")

	var client models.Client
	if err := h.db.Where("id = ?", clientID).First(&client).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Client not found"})
		return
	}

	// Get all active gift types from provider
	var giftTypes []models.GiftType
	h.db.Where("provider_id = ? AND is_active = ?", client.ProviderID, true).
		Order("sort_order ASC").
		Find(&giftTypes)

	// Get client mappings
	var mappings []models.ClientGiftMapping
	h.db.Where("client_id = ?", clientID).Find(&mappings)

	mappingMap := make(map[uuid.UUID]models.ClientGiftMapping)
	for _, m := range mappings {
		mappingMap[m.GiftTypeID] = m
	}

	// Build response
	type GiftWithStatus struct {
		models.GiftType
		IsEnabled   bool     `json:"is_enabled"`
		CustomPrice *float64 `json:"custom_price,omitempty"`
	}

	result := make([]GiftWithStatus, len(giftTypes))
	for i, gt := range giftTypes {
		result[i] = GiftWithStatus{
			GiftType:  gt,
			IsEnabled: true, // Default enabled
		}
		if m, ok := mappingMap[gt.ID]; ok {
			result[i].IsEnabled = m.IsEnabled
			result[i].CustomPrice = m.CustomPrice
		}
	}

	c.JSON(http.StatusOK, gin.H{"gift_types": result})
}

// Client: Toggle gift type availability
func (h *GiftHandler) ToggleClientGift(c *gin.Context) {
	clientID, _ := c.Get("user_id")
	giftTypeID := c.Param("id")

	var req struct {
		IsEnabled   bool     `json:"is_enabled"`
		CustomPrice *float64 `json:"custom_price"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	giftID, _ := uuid.Parse(giftTypeID)

	var mapping models.ClientGiftMapping
	result := h.db.Where("client_id = ? AND gift_type_id = ?", clientID, giftID).First(&mapping)

	if result.Error != nil {
		// Create new mapping
		mapping = models.ClientGiftMapping{
			ClientID:    clientID.(uuid.UUID),
			GiftTypeID:  giftID,
			IsEnabled:   req.IsEnabled,
			CustomPrice: req.CustomPrice,
		}
		h.db.Create(&mapping)
	} else {
		// Update existing
		mapping.IsEnabled = req.IsEnabled
		mapping.CustomPrice = req.CustomPrice
		h.db.Save(&mapping)
	}

	c.JSON(http.StatusOK, gin.H{"mapping": mapping})
}
