package handlers

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/herrylim2001/whitelabel-streaming/internal/models"
	"gorm.io/gorm"
)

type DashboardHandler struct {
	db *gorm.DB
}

func NewDashboardHandler(db *gorm.DB) *DashboardHandler {
	return &DashboardHandler{db: db}
}

// Provider Dashboard
func (h *DashboardHandler) ProviderDashboard(c *gin.Context) {
	providerID, _ := c.Get("user_id")

	now := time.Now()
	startOfDay := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location())
	startOfMonth := time.Date(now.Year(), now.Month(), 1, 0, 0, 0, 0, now.Location())

	// Count clients
	var totalClients, activeClients int64
	h.db.Model(&models.Client{}).Where("provider_id = ?", providerID).Count(&totalClients)
	h.db.Model(&models.Client{}).Where("provider_id = ? AND status = ?", providerID, models.ClientStatusActive).Count(&activeClients)

	// Count hosts (across all clients)
	var totalHosts int64
	h.db.Model(&models.Host{}).
		Joins("JOIN clients ON clients.id = hosts.client_id").
		Where("clients.provider_id = ?", providerID).
		Count(&totalHosts)

	// Count active sessions
	var activeSessions int64
	h.db.Model(&models.LiveSession{}).
		Joins("JOIN hosts ON hosts.id = live_sessions.host_id").
		Joins("JOIN clients ON clients.id = hosts.client_id").
		Where("clients.provider_id = ? AND live_sessions.status = ?", providerID, models.SessionStatusLive).
		Count(&activeSessions)

	// Revenue stats
	var todayRevenue, monthRevenue float64
	h.db.Model(&models.Gift{}).
		Joins("JOIN live_sessions ON live_sessions.id = gifts.session_id").
		Joins("JOIN hosts ON hosts.id = live_sessions.host_id").
		Joins("JOIN clients ON clients.id = hosts.client_id").
		Where("clients.provider_id = ? AND gifts.created_at >= ?", providerID, startOfDay).
		Select("COALESCE(SUM(gifts.provider_fee), 0)").
		Scan(&todayRevenue)

	h.db.Model(&models.Gift{}).
		Joins("JOIN live_sessions ON live_sessions.id = gifts.session_id").
		Joins("JOIN hosts ON hosts.id = live_sessions.host_id").
		Joins("JOIN clients ON clients.id = hosts.client_id").
		Where("clients.provider_id = ? AND gifts.created_at >= ?", providerID, startOfMonth).
		Select("COALESCE(SUM(gifts.provider_fee), 0)").
		Scan(&monthRevenue)

	// Recent clients
	var recentClients []models.Client
	h.db.Where("provider_id = ?", providerID).
		Order("created_at DESC").
		Limit(5).
		Find(&recentClients)

	c.JSON(http.StatusOK, gin.H{
		"stats": gin.H{
			"total_clients":   totalClients,
			"active_clients":  activeClients,
			"total_hosts":     totalHosts,
			"active_sessions": activeSessions,
			"today_revenue":   todayRevenue,
			"month_revenue":   monthRevenue,
		},
		"recent_clients": recentClients,
	})
}

// Client Dashboard
func (h *DashboardHandler) ClientDashboard(c *gin.Context) {
	clientID, _ := c.Get("user_id")

	now := time.Now()
	startOfDay := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location())
	startOfMonth := time.Date(now.Year(), now.Month(), 1, 0, 0, 0, 0, now.Location())

	// Count hosts
	var totalHosts, activeHosts int64
	h.db.Model(&models.Host{}).Where("client_id = ?", clientID).Count(&totalHosts)
	h.db.Model(&models.Host{}).Where("client_id = ? AND status = ?", clientID, models.HostStatusActive).Count(&activeHosts)

	// Count active sessions
	var activeSessions int64
	h.db.Model(&models.LiveSession{}).
		Joins("JOIN hosts ON hosts.id = live_sessions.host_id").
		Where("hosts.client_id = ? AND live_sessions.status = ?", clientID, models.SessionStatusLive).
		Count(&activeSessions)

	// Revenue stats
	var todayRevenue, monthRevenue float64
	h.db.Model(&models.Gift{}).
		Joins("JOIN live_sessions ON live_sessions.id = gifts.session_id").
		Joins("JOIN hosts ON hosts.id = live_sessions.host_id").
		Where("hosts.client_id = ? AND gifts.created_at >= ?", clientID, startOfDay).
		Select("COALESCE(SUM(gifts.client_share), 0)").
		Scan(&todayRevenue)

	h.db.Model(&models.Gift{}).
		Joins("JOIN live_sessions ON live_sessions.id = gifts.session_id").
		Joins("JOIN hosts ON hosts.id = live_sessions.host_id").
		Where("hosts.client_id = ? AND gifts.created_at >= ?", clientID, startOfMonth).
		Select("COALESCE(SUM(gifts.client_share), 0)").
		Scan(&monthRevenue)

	// Pending payouts
	var pendingPayoutsCount int64
	var pendingPayoutsAmount float64
	h.db.Model(&models.Payout{}).
		Joins("JOIN hosts ON hosts.id = payouts.host_id").
		Where("hosts.client_id = ? AND payouts.status = ?", clientID, models.PayoutStatusPending).
		Count(&pendingPayoutsCount)

	h.db.Model(&models.Payout{}).
		Joins("JOIN hosts ON hosts.id = payouts.host_id").
		Where("hosts.client_id = ? AND payouts.status = ?", clientID, models.PayoutStatusPending).
		Select("COALESCE(SUM(payouts.amount_requested), 0)").
		Scan(&pendingPayoutsAmount)

	// Today's sessions count
	var todaySessions int64
	h.db.Model(&models.LiveSession{}).
		Joins("JOIN hosts ON hosts.id = live_sessions.host_id").
		Where("hosts.client_id = ? AND live_sessions.started_at >= ?", clientID, startOfDay).
		Count(&todaySessions)

	// Top hosts (by earnings this month)
	type TopHost struct {
		ID          string  `json:"id"`
		DisplayName string  `json:"display_name"`
		Earnings    float64 `json:"earnings"`
	}
	var topHosts []TopHost
	h.db.Model(&models.LiveSession{}).
		Select("hosts.id, hosts.display_name, COALESCE(SUM(live_sessions.total_earnings), 0) as earnings").
		Joins("JOIN hosts ON hosts.id = live_sessions.host_id").
		Where("hosts.client_id = ? AND live_sessions.ended_at >= ?", clientID, startOfMonth).
		Group("hosts.id, hosts.display_name").
		Order("earnings DESC").
		Limit(5).
		Scan(&topHosts)

	c.JSON(http.StatusOK, gin.H{
		"stats": gin.H{
			"total_hosts":            totalHosts,
			"active_hosts":           activeHosts,
			"active_sessions":        activeSessions,
			"today_sessions":         todaySessions,
			"today_revenue":          todayRevenue,
			"month_revenue":          monthRevenue,
			"pending_payouts_count":  pendingPayoutsCount,
			"pending_payouts_amount": pendingPayoutsAmount,
		},
		"top_hosts": topHosts,
	})
}

// Host Dashboard
func (h *DashboardHandler) HostDashboard(c *gin.Context) {
	hostID, _ := c.Get("user_id")

	now := time.Now()
	startOfDay := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location())
	startOfWeek := startOfDay.AddDate(0, 0, -int(now.Weekday()))
	startOfMonth := time.Date(now.Year(), now.Month(), 1, 0, 0, 0, 0, now.Location())

	var host models.Host
	if err := h.db.Where("id = ?", hostID).First(&host).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Host not found"})
		return
	}

	// Earnings by period
	var todayEarnings, weekEarnings, monthEarnings float64
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

	// Session stats
	var monthSessions int64
	var totalViewers int64
	h.db.Model(&models.LiveSession{}).
		Where("host_id = ? AND started_at >= ?", hostID, startOfMonth).
		Count(&monthSessions)

	h.db.Model(&models.LiveSession{}).
		Where("host_id = ? AND started_at >= ?", hostID, startOfMonth).
		Select("COALESCE(SUM(total_viewers), 0)").
		Scan(&totalViewers)

	// Check for active session
	var activeSession *models.LiveSession
	var session models.LiveSession
	if err := h.db.Where("host_id = ? AND status = ?", hostID, models.SessionStatusLive).First(&session).Error; err == nil {
		activeSession = &session
	}

	// Recent sessions
	var recentSessions []models.LiveSession
	h.db.Where("host_id = ?", hostID).
		Order("created_at DESC").
		Limit(5).
		Find(&recentSessions)

	c.JSON(http.StatusOK, gin.H{
		"host": gin.H{
			"display_name":      host.DisplayName,
			"profile_photo_url": host.ProfilePhotoURL,
			"available_balance": host.AvailableBalance,
			"lifetime_earnings": host.LifetimeEarnings,
		},
		"stats": gin.H{
			"today_earnings":  todayEarnings,
			"week_earnings":   weekEarnings,
			"month_earnings":  monthEarnings,
			"month_sessions":  monthSessions,
			"month_viewers":   totalViewers,
		},
		"active_session":  activeSession,
		"recent_sessions": recentSessions,
	})
}
