package handlers

import (
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/herrylim2001/whitelabel-streaming/internal/models"
	"gorm.io/gorm"
)

type PayoutHandler struct {
	db *gorm.DB
}

func NewPayoutHandler(db *gorm.DB) *PayoutHandler {
	return &PayoutHandler{db: db}
}

// Host: Request a payout
func (h *PayoutHandler) RequestPayout(c *gin.Context) {
	hostID, _ := c.Get("user_id")

	var req struct {
		Amount float64 `json:"amount" binding:"required,gt=0"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	var host models.Host
	if err := h.db.Where("id = ?", hostID).Preload("Client").First(&host).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Host not found"})
		return
	}

	// Check minimum payout
	if req.Amount < host.Client.MinHostPayout {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": fmt.Sprintf("Minimum payout amount is %.2f", host.Client.MinHostPayout),
		})
		return
	}

	// Check available balance
	if req.Amount > host.AvailableBalance {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Insufficient balance"})
		return
	}

	// Check for pending payout
	var pendingCount int64
	h.db.Model(&models.Payout{}).
		Where("host_id = ? AND status IN ?", hostID, []string{"pending", "approved", "processing"}).
		Count(&pendingCount)

	if pendingCount > 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "You have a pending payout request"})
		return
	}

	// Calculate processing fee (example: 1%)
	processingFee := req.Amount * 0.01
	netAmount := req.Amount - processingFee

	payout := models.Payout{
		HostID:          hostID.(uuid.UUID),
		AmountRequested: req.Amount,
		ProcessingFee:   processingFee,
		NetAmount:       netAmount,
		PaymentMethod:   host.PaymentInfo,
		Status:          models.PayoutStatusPending,
		RequestedAt:     time.Now(),
	}

	// Start transaction
	tx := h.db.Begin()

	// Deduct from available balance
	if err := tx.Model(&host).Update("available_balance", gorm.Expr("available_balance - ?", req.Amount)).Error; err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to process payout"})
		return
	}

	// Create payout record
	if err := tx.Create(&payout).Error; err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create payout request"})
		return
	}

	tx.Commit()

	c.JSON(http.StatusCreated, gin.H{
		"payout":  payout,
		"message": "Payout request submitted successfully",
	})
}

// Host: Get payout history
func (h *PayoutHandler) GetHostPayouts(c *gin.Context) {
	hostID, _ := c.Get("user_id")

	var payouts []models.Payout
	h.db.Where("host_id = ?", hostID).Order("created_at DESC").Find(&payouts)

	c.JSON(http.StatusOK, gin.H{"payouts": payouts})
}

// Client: List pending payouts
func (h *PayoutHandler) ListPendingPayouts(c *gin.Context) {
	clientID, _ := c.Get("user_id")

	var payouts []models.Payout
	h.db.Joins("JOIN hosts ON hosts.id = payouts.host_id").
		Where("hosts.client_id = ? AND payouts.status = ?", clientID, models.PayoutStatusPending).
		Preload("Host").
		Order("payouts.requested_at ASC").
		Find(&payouts)

	c.JSON(http.StatusOK, gin.H{"payouts": payouts})
}

// Client: List all payouts
func (h *PayoutHandler) ListClientPayouts(c *gin.Context) {
	clientID, _ := c.Get("user_id")

	var payouts []models.Payout
	query := h.db.Joins("JOIN hosts ON hosts.id = payouts.host_id").
		Where("hosts.client_id = ?", clientID).
		Preload("Host").
		Order("payouts.created_at DESC")

	if status := c.Query("status"); status != "" {
		query = query.Where("payouts.status = ?", status)
	}

	if hostID := c.Query("host_id"); hostID != "" {
		query = query.Where("payouts.host_id = ?", hostID)
	}

	if err := query.Limit(100).Find(&payouts).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch payouts"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"payouts": payouts})
}

// Client: Approve payout
func (h *PayoutHandler) ApprovePayout(c *gin.Context) {
	clientID, _ := c.Get("user_id")
	payoutID := c.Param("id")

	var payout models.Payout
	if err := h.db.Joins("JOIN hosts ON hosts.id = payouts.host_id").
		Where("payouts.id = ? AND hosts.client_id = ?", payoutID, clientID).
		First(&payout).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Payout not found"})
		return
	}

	if payout.Status != models.PayoutStatusPending {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Payout is not pending"})
		return
	}

	now := time.Now()
	approverID := clientID.(uuid.UUID)
	payout.Status = models.PayoutStatusApproved
	payout.ApprovedAt = &now
	payout.ApprovedBy = &approverID

	if err := h.db.Save(&payout).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to approve payout"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"payout": payout, "message": "Payout approved"})
}

// Client: Reject payout
func (h *PayoutHandler) RejectPayout(c *gin.Context) {
	clientID, _ := c.Get("user_id")
	payoutID := c.Param("id")

	var req struct {
		Reason string `json:"reason" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	var payout models.Payout
	if err := h.db.Joins("JOIN hosts ON hosts.id = payouts.host_id").
		Where("payouts.id = ? AND hosts.client_id = ?", payoutID, clientID).
		First(&payout).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Payout not found"})
		return
	}

	if payout.Status != models.PayoutStatusPending {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Payout is not pending"})
		return
	}

	// Refund the amount back to host
	h.db.Model(&models.Host{}).
		Where("id = ?", payout.HostID).
		Update("available_balance", gorm.Expr("available_balance + ?", payout.AmountRequested))

	payout.Status = models.PayoutStatusRejected
	payout.FailureReason = req.Reason

	if err := h.db.Save(&payout).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to reject payout"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"payout": payout, "message": "Payout rejected"})
}

// Client: Mark payout as completed
func (h *PayoutHandler) CompletePayout(c *gin.Context) {
	clientID, _ := c.Get("user_id")
	payoutID := c.Param("id")

	var req struct {
		ReferenceNumber string `json:"reference_number" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	var payout models.Payout
	if err := h.db.Joins("JOIN hosts ON hosts.id = payouts.host_id").
		Where("payouts.id = ? AND hosts.client_id = ?", payoutID, clientID).
		First(&payout).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Payout not found"})
		return
	}

	if payout.Status != models.PayoutStatusApproved && payout.Status != models.PayoutStatusProcessing {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Payout must be approved first"})
		return
	}

	now := time.Now()
	payout.Status = models.PayoutStatusCompleted
	payout.CompletedAt = &now
	payout.ReferenceNumber = req.ReferenceNumber

	if err := h.db.Save(&payout).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to complete payout"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"payout": payout, "message": "Payout completed"})
}
