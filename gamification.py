# -*- coding: utf-8 -*-
class GamificationEngine:
    def get_user_stats(self, user_id: int):
        """
        Returns mocked stats for a user.
        In a real app, this would query the DB.
        """
        return {
            "level": 5,
            "xp": 2450,
            "next_level_xp": 3000,
            "badges": ["🏆 Top Student", "🔥 7 Day Streak", "📚 Bookworm"]
        }

    def get_leaderboard(self, school_id: int):
        """
        Returns mocked leaderboard data.
        """
        return [
            {"rank": 1, "name": "Ahmed Ali", "points": 5200},
            {"rank": 2, "name": "Sarah Khan", "points": 4950},
            {"rank": 3, "name": "Omar Youssef", "points": 4800},
            {"rank": 4, "name": "Laila Mahmoud", "points": 4500},
            {"rank": 5, "name": "Yassin Taha", "points": 4200},
        ]

game_engine = GamificationEngine()
