package handlers

import (
	"crypto/rand"
	"encoding/hex"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/herrylim2001/whitelabel-streaming/internal/models"
	"gorm.io/gorm"
)

type SessionHandler struct {
	db *gorm.DB
}

func NewSessionHandler(db *gorm.DB) *SessionHandler {
	return &SessionHandler{db: db}
}

type CreateSessionRequest struct {
	Title       string     `json:"title" binding:"required"`
	Category    string     `json:"category"`
	ScheduledAt *time.Time `json:"scheduled_at"`
}

// GenerateStreamKey generates a unique stream key
func GenerateStreamKey() string {
	bytes := make([]byte, 16)
	rand.Read(bytes)
	return hex.EncodeToString(bytes)
}

// StartSession creates and starts a new live session (Host)
func (h *SessionHandler) StartSession(c *gin.Context) {
	hostID, _ := c.Get("user_id")

	// Check if host already has an active session
	var activeCount int64
	h.db.Model(&models.LiveSession{}).
		Where("host_id = ? AND status = ?", hostID, models.SessionStatusLive).
		Count(&activeCount)

	if activeCount > 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "You already have an active session"})
		return
	}

	var req CreateSessionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	now := time.Now()
	session := models.LiveSession{
		HostID:    hostID.(uuid.UUID),
		Title:     req.Title,
		Category:  req.Category,
		Status:    models.SessionStatusLive,
		StreamKey: GenerateStreamKey(),
		StartedAt: &now,
	}

	if err := h.db.Create(&session).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create session"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"session":    session,
		"stream_key": session.StreamKey,
	})
}

// EndSession ends an active session (Host)
func (h *SessionHandler) EndSession(c *gin.Context) {
	hostID, _ := c.Get("user_id")
	sessionID := c.Param("id")

	var session models.LiveSession
	if err := h.db.Where("id = ? AND host_id = ?", sessionID, hostID).First(&session).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}

	if session.Status != models.SessionStatusLive {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Session is not live"})
		return
	}

	now := time.Now()
	session.Status = models.SessionStatusEnded
	session.EndedAt = &now

	if session.StartedAt != nil {
		session.DurationSeconds = int(now.Sub(*session.StartedAt).Seconds())
	}

	// Calculate total earnings from gifts
	var totalEarnings float64
	h.db.Model(&models.Gift{}).
		Where("session_id = ?", session.ID).
		Select("COALESCE(SUM(host_earning), 0)").
		Scan(&totalEarnings)

	session.TotalEarnings = totalEarnings

	if err := h.db.Save(&session).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to end session"})
		return
	}

	// Update host earnings
	h.db.Model(&models.Host{}).
		Where("id = ?", hostID).
		Updates(map[string]interface{}{
			"available_balance":  gorm.Expr("available_balance + ?", totalEarnings),
			"lifetime_earnings":  gorm.Expr("lifetime_earnings + ?", totalEarnings),
		})

	c.JSON(http.StatusOK, gin.H{
		"session": session,
		"summary": gin.H{
			"duration_seconds": session.DurationSeconds,
			"total_viewers":    session.TotalViewers,
			"peak_viewers":     session.PeakViewers,
			"total_gifts":      session.TotalGifts,
			"total_earnings":   session.TotalEarnings,
		},
	})
}

// GetActiveSession returns the host's current active session
func (h *SessionHandler) GetActiveSession(c *gin.Context) {
	hostID, _ := c.Get("user_id")

	var session models.LiveSession
	if err := h.db.Where("host_id = ? AND status = ?", hostID, models.SessionStatusLive).
		First(&session).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "No active session"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"session": session})
}

// ListHostSessions returns session history for a host
func (h *SessionHandler) ListHostSessions(c *gin.Context) {
	hostID, _ := c.Get("user_id")

	var sessions []models.LiveSession
	query := h.db.Where("host_id = ?", hostID).Order("created_at DESC")

	if status := c.Query("status"); status != "" {
		query = query.Where("status = ?", status)
	}

	if err := query.Limit(50).Find(&sessions).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch sessions"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"sessions": sessions})
}

// GetSessionDetails returns details of a specific session
func (h *SessionHandler) GetSessionDetails(c *gin.Context) {
	hostID, _ := c.Get("user_id")
	sessionID := c.Param("id")

	var session models.LiveSession
	if err := h.db.Where("id = ? AND host_id = ?", sessionID, hostID).
		Preload("Gifts", func(db *gorm.DB) *gorm.DB {
			return db.Preload("GiftType").Order("created_at DESC").Limit(100)
		}).
		First(&session).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"session": session})
}

// UpdateViewerCount updates viewer count for active session (called by streaming service)
func (h *SessionHandler) UpdateViewerCount(c *gin.Context) {
	sessionID := c.Param("id")

	var req struct {
		CurrentViewers int `json:"current_viewers" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	var session models.LiveSession
	if err := h.db.Where("id = ? AND status = ?", sessionID, models.SessionStatusLive).First(&session).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}

	updates := map[string]interface{}{
		"total_viewers": gorm.Expr("total_viewers + 1"),
	}

	if req.CurrentViewers > session.PeakViewers {
		updates["peak_viewers"] = req.CurrentViewers
	}

	h.db.Model(&session).Updates(updates)

	c.JSON(http.StatusOK, gin.H{"success": true})
}

// Client: List all sessions for their hosts
func (h *SessionHandler) ListClientSessions(c *gin.Context) {
	clientID, _ := c.Get("user_id")

	var sessions []models.LiveSession
	query := h.db.Joins("JOIN hosts ON hosts.id = live_sessions.host_id").
		Where("hosts.client_id = ?", clientID).
		Preload("Host").
		Order("live_sessions.created_at DESC")

	if status := c.Query("status"); status != "" {
		query = query.Where("live_sessions.status = ?", status)
	}

	if hostID := c.Query("host_id"); hostID != "" {
		query = query.Where("live_sessions.host_id = ?", hostID)
	}

	if err := query.Limit(100).Find(&sessions).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch sessions"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"sessions": sessions})
}

// Client: Get active sessions count
func (h *SessionHandler) GetActiveSessions(c *gin.Context) {
	clientID, _ := c.Get("user_id")

	var sessions []models.LiveSession
	h.db.Joins("JOIN hosts ON hosts.id = live_sessions.host_id").
		Where("hosts.client_id = ? AND live_sessions.status = ?", clientID, models.SessionStatusLive).
		Preload("Host").
		Find(&sessions)

	c.JSON(http.StatusOK, gin.H{
		"active_count": len(sessions),
		"sessions":     sessions,
	})
}
