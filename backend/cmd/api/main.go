package main

import (
	"log"

	"github.com/gin-gonic/gin"
	"github.com/herrylim2001/whitelabel-streaming/internal/config"
	"github.com/herrylim2001/whitelabel-streaming/internal/database"
	"github.com/herrylim2001/whitelabel-streaming/internal/handlers"
	"github.com/herrylim2001/whitelabel-streaming/internal/middleware"
	"github.com/herrylim2001/whitelabel-streaming/internal/services"
)

func main() {
	// Load configuration
	cfg := config.Load()

	// Connect to database
	db, err := database.Connect(cfg)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Run migrations
	if err := database.Migrate(); err != nil {
		log.Fatalf("Failed to run migrations: %v", err)
	}

	// Initialize services
	authService := services.NewAuthService(db, cfg)

	// Initialize handlers
	authHandler := handlers.NewAuthHandler(authService)
	clientHandler := handlers.NewClientHandler(db)
	hostHandler := handlers.NewHostHandler(db)
	sessionHandler := handlers.NewSessionHandler(db)
	payoutHandler := handlers.NewPayoutHandler(db)
	giftHandler := handlers.NewGiftHandler(db)
	dashboardHandler := handlers.NewDashboardHandler(db)

	// Setup Gin
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()

	// CORS middleware
	r.Use(middleware.CORSMiddleware(cfg.CORSOrigins))

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// API routes
	api := r.Group("/api/v1")
	{
		// Auth routes (public)
		auth := api.Group("/auth")
		{
			auth.POST("/login", authHandler.Login)
			auth.POST("/register/provider", authHandler.RegisterProvider)
		}

		// Protected routes
		protected := api.Group("")
		protected.Use(middleware.AuthMiddleware(cfg))
		{
			// Auth
			protected.GET("/auth/me", authHandler.GetMe)

			// ========== PROVIDER ROUTES ==========
			provider := protected.Group("/provider")
			provider.Use(middleware.RoleMiddleware(middleware.RoleProvider))
			{
				// Dashboard
				provider.GET("/dashboard", dashboardHandler.ProviderDashboard)

				// Clients
				provider.GET("/clients", clientHandler.ListClients)
				provider.POST("/clients", clientHandler.CreateClient)
				provider.GET("/clients/:id", clientHandler.GetClient)
				provider.PUT("/clients/:id", clientHandler.UpdateClient)
				provider.DELETE("/clients/:id", clientHandler.DeleteClient)
				provider.POST("/clients/:id/activate", clientHandler.ActivateClient)
				provider.POST("/clients/:id/suspend", clientHandler.SuspendClient)

				// Gift Types
				provider.GET("/gifts", giftHandler.ListGiftTypes)
				provider.POST("/gifts", giftHandler.CreateGiftType)
				provider.PUT("/gifts/:id", giftHandler.UpdateGiftType)
				provider.DELETE("/gifts/:id", giftHandler.DeleteGiftType)
			}

			// ========== CLIENT ROUTES ==========
			client := protected.Group("/client")
			client.Use(middleware.RoleMiddleware(middleware.RoleClient))
			{
				// Dashboard
				client.GET("/dashboard", dashboardHandler.ClientDashboard)

				// Hosts
				client.GET("/hosts", hostHandler.ListHosts)
				client.POST("/hosts", hostHandler.CreateHost)
				client.GET("/hosts/:id", hostHandler.GetHost)
				client.PUT("/hosts/:id", hostHandler.UpdateHost)
				client.DELETE("/hosts/:id", hostHandler.DeleteHost)
				client.POST("/hosts/:id/activate", hostHandler.ActivateHost)

				// Sessions
				client.GET("/sessions", sessionHandler.ListClientSessions)
				client.GET("/sessions/active", sessionHandler.GetActiveSessions)

				// Payouts
				client.GET("/payouts", payoutHandler.ListClientPayouts)
				client.GET("/payouts/pending", payoutHandler.ListPendingPayouts)
				client.POST("/payouts/:id/approve", payoutHandler.ApprovePayout)
				client.POST("/payouts/:id/reject", payoutHandler.RejectPayout)
				client.POST("/payouts/:id/complete", payoutHandler.CompletePayout)

				// Gifts
				client.GET("/gifts", giftHandler.GetClientGiftTypes)
				client.PUT("/gifts/:id/toggle", giftHandler.ToggleClientGift)
			}

			// ========== HOST ROUTES ==========
			host := protected.Group("/host")
			host.Use(middleware.RoleMiddleware(middleware.RoleHost))
			{
				// Dashboard
				host.GET("/dashboard", dashboardHandler.HostDashboard)

				// Profile
				host.GET("/profile", hostHandler.GetHostProfile)
				host.PUT("/profile", hostHandler.UpdateHostProfile)

				// Earnings
				host.GET("/earnings", hostHandler.GetHostEarnings)

				// Sessions
				host.GET("/sessions", sessionHandler.ListHostSessions)
				host.GET("/sessions/active", sessionHandler.GetActiveSession)
				host.GET("/sessions/:id", sessionHandler.GetSessionDetails)
				host.POST("/sessions/start", sessionHandler.StartSession)
				host.POST("/sessions/:id/end", sessionHandler.EndSession)

				// Payouts
				host.GET("/payouts", payoutHandler.GetHostPayouts)
				host.POST("/payouts", payoutHandler.RequestPayout)
			}
		}

		// Public/Webhook routes
		api.POST("/sessions/:session_id/gifts", giftHandler.SendGift)
		api.PUT("/sessions/:id/viewers", sessionHandler.UpdateViewerCount)
	}

	// Start server
	addr := cfg.ServerHost + ":" + cfg.ServerPort
	log.Printf("Server starting on %s", addr)
	if err := r.Run(addr); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
