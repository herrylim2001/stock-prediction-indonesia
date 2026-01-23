"""
Database module untuk manage data talent dan livestream
Menggunakan in-memory storage untuk prototype
"""
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class Database:
    def __init__(self):
        # In-memory storage untuk prototype
        self.talents = {}
        self.livestreams = {}
        self.viewers = {}
        self.stats = {}

        # Seed data untuk demo
        self._seed_data()

    def _seed_data(self):
        """Tambahkan sample data untuk demo"""
        sample_talents = [
            {
                "id": str(uuid.uuid4()),
                "name": "Sarah Beauty",
                "username": "sarah_beauty",
                "avatar": "https://i.pravatar.cc/150?img=1",
                "status": "online",
                "followers": 12500,
                "total_viewers": 45230,
                "total_diamonds": 8900,
                "level": 25,
                "bio": "Beauty & Lifestyle Content Creator"
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
                "level": 42,
                "bio": "Pro Gamer & Streamer"
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
                "level": 18,
                "bio": "Singer & Music Lover"
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
                "level": 35,
                "bio": "Fitness Coach & Motivator"
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
                "level": 28,
                "bio": "Chef & Cooking Enthusiast"
            }
        ]

        for talent in sample_talents:
            self.talents[talent['id']] = talent

            # Buat livestream untuk talent yang sedang live
            if talent['status'] == 'live':
                livestream_id = str(uuid.uuid4())
                self.livestreams[livestream_id] = {
                    "id": livestream_id,
                    "talent_id": talent['id'],
                    "talent_name": talent['name'],
                    "talent_avatar": talent['avatar'],
                    "title": f"{talent['name']}'s Live Stream",
                    "thumbnail": f"https://picsum.photos/seed/{livestream_id}/400/300",
                    "viewers": 0,
                    "likes": 0,
                    "diamonds": 0,
                    "started_at": datetime.now().isoformat(),
                    "status": "live"
                }

    # Talent Operations
    def get_all_talents(self) -> List[Dict]:
        """Get semua talent"""
        return list(self.talents.values())

    def get_talent_by_id(self, talent_id: str) -> Optional[Dict]:
        """Get talent by ID"""
        return self.talents.get(talent_id)

    def update_talent(self, talent_id: str, data: Dict) -> Optional[Dict]:
        """Update talent data"""
        if talent_id in self.talents:
            self.talents[talent_id].update(data)
            return self.talents[talent_id]
        return None

    def update_talent_status(self, talent_id: str, status: str) -> Optional[Dict]:
        """Update talent status (online, offline, live)"""
        if talent_id in self.talents:
            self.talents[talent_id]['status'] = status
            return self.talents[talent_id]
        return None

    # Livestream Operations
    def get_all_livestreams(self) -> List[Dict]:
        """Get semua active livestreams"""
        return [ls for ls in self.livestreams.values() if ls['status'] == 'live']

    def get_livestream_by_id(self, livestream_id: str) -> Optional[Dict]:
        """Get livestream by ID"""
        return self.livestreams.get(livestream_id)

    def create_livestream(self, talent_id: str, title: str) -> Optional[Dict]:
        """Buat livestream baru"""
        if talent_id not in self.talents:
            return None

        talent = self.talents[talent_id]
        livestream_id = str(uuid.uuid4())

        livestream = {
            "id": livestream_id,
            "talent_id": talent_id,
            "talent_name": talent['name'],
            "talent_avatar": talent['avatar'],
            "title": title,
            "thumbnail": f"https://picsum.photos/seed/{livestream_id}/400/300",
            "viewers": 0,
            "likes": 0,
            "diamonds": 0,
            "started_at": datetime.now().isoformat(),
            "status": "live"
        }

        self.livestreams[livestream_id] = livestream
        self.update_talent_status(talent_id, 'live')

        return livestream

    def end_livestream(self, livestream_id: str) -> bool:
        """End livestream"""
        if livestream_id in self.livestreams:
            livestream = self.livestreams[livestream_id]
            livestream['status'] = 'ended'
            livestream['ended_at'] = datetime.now().isoformat()

            # Update talent status
            self.update_talent_status(livestream['talent_id'], 'offline')
            return True
        return False

    def increment_viewer(self, livestream_id: str) -> Optional[Dict]:
        """Tambah viewer count"""
        if livestream_id in self.livestreams:
            self.livestreams[livestream_id]['viewers'] += 1
            return self.livestreams[livestream_id]
        return None

    def decrement_viewer(self, livestream_id: str) -> Optional[Dict]:
        """Kurangi viewer count"""
        if livestream_id in self.livestreams:
            if self.livestreams[livestream_id]['viewers'] > 0:
                self.livestreams[livestream_id]['viewers'] -= 1
            return self.livestreams[livestream_id]
        return None

    def add_like(self, livestream_id: str) -> Optional[Dict]:
        """Tambah like"""
        if livestream_id in self.livestreams:
            self.livestreams[livestream_id]['likes'] += 1
            return self.livestreams[livestream_id]
        return None

    def add_diamonds(self, livestream_id: str, amount: int) -> Optional[Dict]:
        """Tambah diamonds (gifts)"""
        if livestream_id in self.livestreams:
            self.livestreams[livestream_id]['diamonds'] += amount

            # Update talent total diamonds
            talent_id = self.livestreams[livestream_id]['talent_id']
            if talent_id in self.talents:
                self.talents[talent_id]['total_diamonds'] += amount

            return self.livestreams[livestream_id]
        return None

    # Stats Operations
    def get_platform_stats(self) -> Dict:
        """Get platform statistics"""
        total_talents = len(self.talents)
        active_livestreams = len([ls for ls in self.livestreams.values() if ls['status'] == 'live'])
        total_viewers = sum(ls['viewers'] for ls in self.livestreams.values() if ls['status'] == 'live')
        total_diamonds = sum(t['total_diamonds'] for t in self.talents.values())

        return {
            "total_talents": total_talents,
            "active_livestreams": active_livestreams,
            "total_viewers": total_viewers,
            "total_diamonds": total_diamonds,
            "online_talents": len([t for t in self.talents.values() if t['status'] in ['online', 'live']])
        }

# Global database instance
db = Database()
