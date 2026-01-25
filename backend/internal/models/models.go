package models

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// BaseModel contains common fields for all models
type BaseModel struct {
	ID        uuid.UUID      `gorm:"type:uuid;primary_key;default:gen_random_uuid()" json:"id"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

// Provider represents the platform owner / super admin
type Provider struct {
	BaseModel
	Name        string   `gorm:"size:255;not null" json:"name"`
	Email       string   `gorm:"size:255;uniqueIndex;not null" json:"email"`
	Password    string   `gorm:"size:255;not null" json:"-"`
	Phone       string   `gorm:"size:50" json:"phone"`
	CompanyName string   `gorm:"size:255" json:"company_name"`
	LogoURL     string   `gorm:"size:500" json:"logo_url"`
	Settings    JSON     `gorm:"type:jsonb;default:'{}'" json:"settings"`
	Clients     []Client `gorm:"foreignKey:ProviderID" json:"clients,omitempty"`
	Plans       []Plan   `gorm:"foreignKey:ProviderID" json:"plans,omitempty"`
	GiftTypes   []GiftType `gorm:"foreignKey:ProviderID" json:"gift_types,omitempty"`
}

// Plan represents subscription plans offered by provider
type Plan struct {
	BaseModel
	ProviderID           uuid.UUID `gorm:"type:uuid;not null" json:"provider_id"`
	Name                 string    `gorm:"size:100;not null" json:"name"`
	Description          string    `gorm:"type:text" json:"description"`
	MaxHosts             int       `gorm:"default:10" json:"max_hosts"`
	MaxConcurrentStreams int       `gorm:"default:5" json:"max_concurrent_streams"`
	StorageGB            int       `gorm:"default:50" json:"storage_gb"`
	Features             JSON      `gorm:"type:jsonb;default:'{}'" json:"features"`
	PriceMonthly         float64   `gorm:"type:decimal(10,2)" json:"price_monthly"`
	PriceYearly          float64   `gorm:"type:decimal(10,2)" json:"price_yearly"`
	IsActive             bool      `gorm:"default:true" json:"is_active"`
	Provider             Provider  `gorm:"foreignKey:ProviderID" json:"-"`
	Clients              []Client  `gorm:"foreignKey:PlanID" json:"clients,omitempty"`
}

// ClientStatus represents the status of a client
type ClientStatus string

const (
	ClientStatusPending    ClientStatus = "pending"
	ClientStatusActive     ClientStatus = "active"
	ClientStatusSuspended  ClientStatus = "suspended"
	ClientStatusTerminated ClientStatus = "terminated"
)

// ClientBranding represents branding configuration
type ClientBranding struct {
	LogoURL        string `json:"logo_url"`
	PrimaryColor   string `json:"primary_color"`
	SecondaryColor string `json:"secondary_color"`
	CustomDomain   string `json:"custom_domain"`
}

// Client represents a brand/operator using the platform
type Client struct {
	BaseModel
	ProviderID          uuid.UUID    `gorm:"type:uuid;not null" json:"provider_id"`
	PlanID              uuid.UUID    `gorm:"type:uuid" json:"plan_id"`
	CompanyName         string       `gorm:"size:255;not null" json:"company_name"`
	ContactName         string       `gorm:"size:255" json:"contact_name"`
	ContactEmail        string       `gorm:"size:255;uniqueIndex;not null" json:"contact_email"`
	ContactPhone        string       `gorm:"size:50" json:"contact_phone"`
	Password            string       `gorm:"size:255;not null" json:"-"`
	Branding            JSON         `gorm:"type:jsonb;default:'{}'" json:"branding"`
	RevenueSharePercent float64      `gorm:"type:decimal(5,2);default:70" json:"revenue_share_percent"`
	MinHostPayout       float64      `gorm:"type:decimal(10,2);default:50" json:"min_host_payout"`
	Status              ClientStatus `gorm:"size:20;default:'pending'" json:"status"`
	Settings            JSON         `gorm:"type:jsonb;default:'{}'" json:"settings"`
	Provider            Provider     `gorm:"foreignKey:ProviderID" json:"-"`
	Plan                Plan         `gorm:"foreignKey:PlanID" json:"plan,omitempty"`
	Hosts               []Host       `gorm:"foreignKey:ClientID" json:"hosts,omitempty"`
}

// HostStatus represents the status of a host
type HostStatus string

const (
	HostStatusPending    HostStatus = "pending"
	HostStatusActive     HostStatus = "active"
	HostStatusSuspended  HostStatus = "suspended"
	HostStatusTerminated HostStatus = "terminated"
)

// PaymentInfo represents host payment information
type PaymentInfo struct {
	Type          string `json:"type"` // bank, ewallet
	BankName      string `json:"bank_name"`
	AccountNumber string `json:"account_number"`
	AccountHolder string `json:"account_holder"`
}

// Host represents a talent/streamer
type Host struct {
	BaseModel
	ClientID         uuid.UUID   `gorm:"type:uuid;not null" json:"client_id"`
	Email            string      `gorm:"size:255;not null" json:"email"`
	Password         string      `gorm:"size:255;not null" json:"-"`
	DisplayName      string      `gorm:"size:255;not null" json:"display_name"`
	LegalName        string      `gorm:"size:255" json:"legal_name"`
	ProfilePhotoURL  string      `gorm:"size:500" json:"profile_photo_url"`
	Bio              string      `gorm:"type:text" json:"bio"`
	SocialLinks      JSON        `gorm:"type:jsonb;default:'{}'" json:"social_links"`
	PayoutRatePercent float64    `gorm:"type:decimal(5,2);default:70" json:"payout_rate_percent"`
	PaymentInfo      JSON        `gorm:"type:jsonb;default:'{}'" json:"payment_info"`
	AvailableBalance float64     `gorm:"type:decimal(12,2);default:0" json:"available_balance"`
	LifetimeEarnings float64     `gorm:"type:decimal(12,2);default:0" json:"lifetime_earnings"`
	Status           HostStatus  `gorm:"size:20;default:'pending'" json:"status"`
	VerifiedAt       *time.Time  `json:"verified_at"`
	Client           Client      `gorm:"foreignKey:ClientID" json:"-"`
	LiveSessions     []LiveSession `gorm:"foreignKey:HostID" json:"live_sessions,omitempty"`
	Payouts          []Payout    `gorm:"foreignKey:HostID" json:"payouts,omitempty"`
}

// SessionStatus represents the status of a live session
type SessionStatus string

const (
	SessionStatusScheduled SessionStatus = "scheduled"
	SessionStatusLive      SessionStatus = "live"
	SessionStatusEnded     SessionStatus = "ended"
	SessionStatusCancelled SessionStatus = "cancelled"
)

// LiveSession represents a streaming session
type LiveSession struct {
	BaseModel
	HostID          uuid.UUID     `gorm:"type:uuid;not null" json:"host_id"`
	Title           string        `gorm:"size:255;not null" json:"title"`
	Category        string        `gorm:"size:100" json:"category"`
	Status          SessionStatus `gorm:"size:20;default:'scheduled'" json:"status"`
	StreamKey       string        `gorm:"size:100;uniqueIndex" json:"stream_key"`
	ScheduledAt     *time.Time    `json:"scheduled_at"`
	StartedAt       *time.Time    `json:"started_at"`
	EndedAt         *time.Time    `json:"ended_at"`
	DurationSeconds int           `gorm:"default:0" json:"duration_seconds"`
	PeakViewers     int           `gorm:"default:0" json:"peak_viewers"`
	TotalViewers    int           `gorm:"default:0" json:"total_viewers"`
	TotalGifts      int           `gorm:"default:0" json:"total_gifts"`
	TotalGiftValue  float64       `gorm:"type:decimal(12,2);default:0" json:"total_gift_value"`
	TotalEarnings   float64       `gorm:"type:decimal(12,2);default:0" json:"total_earnings"`
	RecordingURL    string        `gorm:"size:500" json:"recording_url"`
	ThumbnailURL    string        `gorm:"size:500" json:"thumbnail_url"`
	Metadata        JSON          `gorm:"type:jsonb;default:'{}'" json:"metadata"`
	Host            Host          `gorm:"foreignKey:HostID" json:"host,omitempty"`
	Gifts           []Gift        `gorm:"foreignKey:SessionID" json:"gifts,omitempty"`
}

// GiftType represents a type of virtual gift
type GiftType struct {
	BaseModel
	ProviderID   uuid.UUID `gorm:"type:uuid;not null" json:"provider_id"`
	Name         string    `gorm:"size:100;not null" json:"name"`
	IconURL      string    `gorm:"size:500" json:"icon_url"`
	AnimationURL string    `gorm:"size:500" json:"animation_url"`
	Price        float64   `gorm:"type:decimal(10,2);not null" json:"price"`
	SortOrder    int       `gorm:"default:0" json:"sort_order"`
	IsActive     bool      `gorm:"default:true" json:"is_active"`
	Provider     Provider  `gorm:"foreignKey:ProviderID" json:"-"`
}

// Gift represents a gift transaction during a live session
type Gift struct {
	BaseModel
	SessionID   uuid.UUID `gorm:"type:uuid;not null" json:"session_id"`
	GiftTypeID  uuid.UUID `gorm:"type:uuid;not null" json:"gift_type_id"`
	ViewerID    string    `gorm:"size:255" json:"viewer_id"`
	Quantity    int       `gorm:"default:1" json:"quantity"`
	UnitPrice   float64   `gorm:"type:decimal(10,2)" json:"unit_price"`
	TotalValue  float64   `gorm:"type:decimal(10,2)" json:"total_value"`
	ProviderFee float64   `gorm:"type:decimal(10,2)" json:"provider_fee"`
	ClientShare float64   `gorm:"type:decimal(10,2)" json:"client_share"`
	HostEarning float64   `gorm:"type:decimal(10,2)" json:"host_earning"`
	Session     LiveSession `gorm:"foreignKey:SessionID" json:"-"`
	GiftType    GiftType  `gorm:"foreignKey:GiftTypeID" json:"gift_type,omitempty"`
}

// PayoutStatus represents the status of a payout
type PayoutStatus string

const (
	PayoutStatusPending    PayoutStatus = "pending"
	PayoutStatusApproved   PayoutStatus = "approved"
	PayoutStatusProcessing PayoutStatus = "processing"
	PayoutStatusCompleted  PayoutStatus = "completed"
	PayoutStatusRejected   PayoutStatus = "rejected"
	PayoutStatusFailed     PayoutStatus = "failed"
)

// Payout represents a payout request from host
type Payout struct {
	BaseModel
	HostID          uuid.UUID    `gorm:"type:uuid;not null" json:"host_id"`
	AmountRequested float64      `gorm:"type:decimal(12,2);not null" json:"amount_requested"`
	ProcessingFee   float64      `gorm:"type:decimal(10,2);default:0" json:"processing_fee"`
	NetAmount       float64      `gorm:"type:decimal(12,2)" json:"net_amount"`
	PaymentMethod   JSON         `gorm:"type:jsonb;default:'{}'" json:"payment_method"`
	Status          PayoutStatus `gorm:"size:20;default:'pending'" json:"status"`
	RequestedAt     time.Time    `gorm:"not null" json:"requested_at"`
	ApprovedAt      *time.Time   `json:"approved_at"`
	ApprovedBy      *uuid.UUID   `gorm:"type:uuid" json:"approved_by"`
	ProcessedAt     *time.Time   `json:"processed_at"`
	CompletedAt     *time.Time   `json:"completed_at"`
	ReferenceNumber string       `gorm:"size:100" json:"reference_number"`
	FailureReason   string       `gorm:"size:500" json:"failure_reason"`
	Notes           string       `gorm:"type:text" json:"notes"`
	Host            Host         `gorm:"foreignKey:HostID" json:"host,omitempty"`
}

// ClientGiftMapping represents which gifts are enabled for a client
type ClientGiftMapping struct {
	BaseModel
	ClientID    uuid.UUID `gorm:"type:uuid;not null" json:"client_id"`
	GiftTypeID  uuid.UUID `gorm:"type:uuid;not null" json:"gift_type_id"`
	IsEnabled   bool      `gorm:"default:true" json:"is_enabled"`
	CustomPrice *float64  `gorm:"type:decimal(10,2)" json:"custom_price"`
	Client      Client    `gorm:"foreignKey:ClientID" json:"-"`
	GiftType    GiftType  `gorm:"foreignKey:GiftTypeID" json:"gift_type,omitempty"`
}

// JSON type for PostgreSQL JSONB
type JSON map[string]interface{}
