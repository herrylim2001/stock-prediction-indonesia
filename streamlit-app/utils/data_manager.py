"""
Data Manager untuk Streamlit Livestream App
Manages talents dan livestreams data
"""
import streamlit as st
from datetime import datetime
import uuid
import random

class DataManager:
    """Singleton class untuk manage data"""

    def __init__(self):
        self._init_session_state()

    def _init_session_state(self):
        """Initialize session state dengan sample data"""
        if 'talents' not in st.session_state:
            st.session_state.talents = self._create_sample_talents()

        if 'livestreams' not in st.session_state:
            st.session_state.livestreams = self._create_sample_livestreams()

        if 'data_initialized' not in st.session_state:
            st.session_state.data_initialized = True

    def _create_sample_talents(self):
        """Create sample talent data"""
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "Sarah Beauty",
                "username": "sarah_beauty",
                "avatar": "https://i.pravatar.cc/150?img=1",
                "status": "online",
                "followers": 12500,
                "total_viewers": 45230,
                "total_diamonds": 8900,
                "total_gifts": 1250,
                "level": 25,
                "bio": "Beauty & Lifestyle Content Creator",
                "join_date": "2024-01-15",
                "total_streams": 156,
                "avg_viewers": 290
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Mike Gaming",
                "username": "mike_gamer",
                "avatar": "https://i.pravatar.cc/150?img=12",
                "status": "live",
                "followers": 28900,
                "total_viewers": 125600,
                "total_diamonds": 15600,
                "total_gifts": 2100,
                "level": 42,
                "bio": "Pro Gamer & Streamer",
                "join_date": "2023-08-20",
                "total_streams": 312,
                "avg_viewers": 403
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Lisa Music",
                "username": "lisa_sings",
                "avatar": "https://i.pravatar.cc/150?img=5",
                "status": "offline",
                "followers": 8200,
                "total_viewers": 32100,
                "total_diamonds": 6500,
                "total_gifts": 890,
                "level": 18,
                "bio": "Singer & Music Lover",
                "join_date": "2024-03-10",
                "total_streams": 98,
                "avg_viewers": 328
            },
            {
                "id": str(uuid.uuid4()),
                "name": "David Fitness",
                "username": "david_fit",
                "avatar": "https://i.pravatar.cc/150?img=8",
                "status": "live",
                "followers": 19800,
                "total_viewers": 67400,
                "total_diamonds": 11200,
                "total_gifts": 1680,
                "level": 35,
                "bio": "Fitness Coach & Motivator",
                "join_date": "2023-11-05",
                "total_streams": 203,
                "avg_viewers": 332
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Anna Cook",
                "username": "anna_cooks",
                "avatar": "https://i.pravatar.cc/150?img=9",
                "status": "online",
                "followers": 15600,
                "total_viewers": 53200,
                "total_diamonds": 9800,
                "total_gifts": 1420,
                "level": 28,
                "bio": "Chef & Cooking Enthusiast",
                "join_date": "2024-02-01",
                "total_streams": 145,
                "avg_viewers": 367
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Ryan Tech",
                "username": "ryan_tech",
                "avatar": "https://i.pravatar.cc/150?img=13",
                "status": "offline",
                "followers": 22100,
                "total_viewers": 89300,
                "total_diamonds": 13400,
                "total_gifts": 1890,
                "level": 38,
                "bio": "Tech Review & Tutorials",
                "join_date": "2023-09-15",
                "total_streams": 267,
                "avg_viewers": 335
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Emma Art",
                "username": "emma_artist",
                "avatar": "https://i.pravatar.cc/150?img=10",
                "status": "online",
                "followers": 11800,
                "total_viewers": 41200,
                "total_diamonds": 7600,
                "total_gifts": 1120,
                "level": 22,
                "bio": "Digital Artist & Illustrator",
                "join_date": "2024-01-28",
                "total_streams": 124,
                "avg_viewers": 332
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Jack Comedy",
                "username": "jack_funny",
                "avatar": "https://i.pravatar.cc/150?img=14",
                "status": "offline",
                "followers": 17500,
                "total_viewers": 62800,
                "total_diamonds": 10100,
                "total_gifts": 1540,
                "level": 31,
                "bio": "Stand-up Comedian",
                "join_date": "2023-12-10",
                "total_streams": 189,
                "avg_viewers": 332
            }
        ]

    def _create_sample_livestreams(self):
        """Create sample livestream data"""
        live_talents = [t for t in st.session_state.talents if t['status'] == 'live']

        livestreams = []
        for talent in live_talents:
            livestream = {
                "id": str(uuid.uuid4()),
                "talent_id": talent['id'],
                "talent_name": talent['name'],
                "talent_avatar": talent['avatar'],
                "talent_username": talent['username'],
                "title": f"{talent['name']}'s Live Stream",
                "description": f"Join {talent['name']} live! {talent['bio']}",
                "thumbnail": f"https://picsum.photos/seed/{talent['id']}/400/300",
                "viewers": random.randint(150, 500),
                "likes": random.randint(500, 2000),
                "diamonds": random.randint(100, 800),
                "comments": random.randint(300, 1500),
                "started_at": datetime.now().isoformat(),
                "status": "live",
                "category": random.choice(["Gaming", "Lifestyle", "Music", "Fitness", "Cooking", "Tech"]),
                "tags": random.sample(["trending", "new", "popular", "featured", "top"], k=2)
            }
            livestreams.append(livestream)

        return livestreams

    # Talent Operations
    def get_all_talents(self):
        """Get all talents"""
        return st.session_state.talents

    def get_talent_by_id(self, talent_id):
        """Get talent by ID"""
        return next((t for t in st.session_state.talents if t['id'] == talent_id), None)

    def update_talent(self, talent_id, updates):
        """Update talent data"""
        for i, talent in enumerate(st.session_state.talents):
            if talent['id'] == talent_id:
                st.session_state.talents[i].update(updates)
                return True
        return False

    def update_talent_status(self, talent_id, status):
        """Update talent status"""
        return self.update_talent(talent_id, {'status': status})

    def get_talents_by_status(self, status):
        """Get talents by status"""
        return [t for t in st.session_state.talents if t['status'] == status]

    def add_talent(self, talent_data):
        """Add new talent"""
        talent_data['id'] = str(uuid.uuid4())
        st.session_state.talents.append(talent_data)
        return talent_data

    def delete_talent(self, talent_id):
        """Delete talent"""
        st.session_state.talents = [t for t in st.session_state.talents if t['id'] != talent_id]
        return True

    # Livestream Operations
    def get_all_livestreams(self):
        """Get all active livestreams"""
        return [ls for ls in st.session_state.livestreams if ls['status'] == 'live']

    def get_livestream_by_id(self, livestream_id):
        """Get livestream by ID"""
        return next((ls for ls in st.session_state.livestreams if ls['id'] == livestream_id), None)

    def create_livestream(self, talent_id, title, description=""):
        """Create new livestream"""
        talent = self.get_talent_by_id(talent_id)
        if not talent:
            return None

        livestream = {
            "id": str(uuid.uuid4()),
            "talent_id": talent_id,
            "talent_name": talent['name'],
            "talent_avatar": talent['avatar'],
            "talent_username": talent['username'],
            "title": title,
            "description": description or f"Join {talent['name']} live!",
            "thumbnail": f"https://picsum.photos/seed/{talent_id}/400/300",
            "viewers": 0,
            "likes": 0,
            "diamonds": 0,
            "comments": 0,
            "started_at": datetime.now().isoformat(),
            "status": "live",
            "category": "General",
            "tags": []
        }

        st.session_state.livestreams.append(livestream)
        self.update_talent_status(talent_id, 'live')

        return livestream

    def end_livestream(self, livestream_id):
        """End livestream"""
        for i, ls in enumerate(st.session_state.livestreams):
            if ls['id'] == livestream_id:
                st.session_state.livestreams[i]['status'] = 'ended'
                st.session_state.livestreams[i]['ended_at'] = datetime.now().isoformat()

                # Update talent status
                self.update_talent_status(ls['talent_id'], 'offline')
                return True
        return False

    def update_livestream_stats(self, livestream_id, stat_type, increment=1):
        """Update livestream statistics"""
        for i, ls in enumerate(st.session_state.livestreams):
            if ls['id'] == livestream_id:
                st.session_state.livestreams[i][stat_type] += increment
                return True
        return False

    # Statistics
    def get_platform_stats(self):
        """Get platform-wide statistics"""
        talents = self.get_all_talents()
        livestreams = self.get_all_livestreams()

        return {
            "total_talents": len(talents),
            "online_talents": len([t for t in talents if t['status'] in ['online', 'live']]),
            "active_livestreams": len(livestreams),
            "total_viewers": sum(ls['viewers'] for ls in livestreams),
            "total_diamonds": sum(t['total_diamonds'] for t in talents),
            "total_followers": sum(t['followers'] for t in talents),
            "total_streams": sum(t.get('total_streams', 0) for t in talents),
            "avg_viewers_per_stream": sum(t.get('avg_viewers', 0) for t in talents) / len(talents) if talents else 0
        }

    def get_top_talents(self, metric='total_diamonds', limit=5):
        """Get top talents by metric"""
        talents = sorted(self.get_all_talents(), key=lambda x: x.get(metric, 0), reverse=True)
        return talents[:limit]

    def get_talent_growth_data(self):
        """Get talent growth data for charts"""
        # Simulated growth data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        data = {
            'Month': months,
            'New Talents': [5, 8, 12, 10, 15, 18],
            'Active Talents': [20, 25, 32, 38, 45, 52]
        }
        return data

    def get_revenue_data(self):
        """Get revenue data for charts"""
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        data = {
            'Month': months,
            'Diamonds': [15000, 18500, 22000, 25800, 31200, 38900],
            'Gifts': [8500, 10200, 13400, 16700, 20100, 24500]
        }
        return data

# Singleton instance
@st.cache_resource
def get_data_manager():
    """Get DataManager singleton instance"""
    return DataManager()
