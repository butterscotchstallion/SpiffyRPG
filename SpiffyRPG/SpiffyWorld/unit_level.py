# -*- coding: utf-8 -*-
class UnitLevel:
    """
    Functionality related to how much xp a unit has
    """
    def get_level_by_xp(self, total_experience):
        player_level = 1
        levels = self.get_levels()
 
        for level, experience_needed in levels:
            if total_experience > experience_needed:
                player_level = level

        """ If this player is max level or higher, just choose last one """
        if total_experience > levels[-1][1]:
            player_level = levels[-1][0]

        return player_level

    def get_xp_for_level(self, player_level):
        xp = 1
        levels = self.get_levels()
 
        for level, experience_needed in levels:
            if level == player_level:
                return experience_needed

        return player_level

    def get_xp_for_next_level(self, level):
        xp = 0
        levels = self.get_levels()

        for xp_level, req_xp in levels:
            if xp_level == (level+1):
                xp = req_xp
                break

        return xp

    def get_levels(self):
        return [(1, 0),
                (2, 100),
                (3, 200),
                (4, 300),
                (5, 400),
                (6, 1000),
                (7, 1500),
                (8, 2500),
                (9, 3500),
                (10, 5000),
                (11, 6500),
                (12, 8000),
                (13, 9500),
                (14, 10500),
                (15, 12000),
                (16, 15000),
                (17, 18000),
                (18, 21000),
                (19, 24000),
                (20, 27000),
                (21, 30000),
                (22, 33000),
                (24, 36000),
                (25, 39000),
                (26, 42000),
                (27, 45000),
                (28, 48000),
                (29, 51000),
                (30, 54000),
                (31, 57000),
                (32, 60000),
                (33, 63000),
                (34, 66000),
                (35, 69000),
                (36, 70000),
                (37, 73000),
                (38, 76000),
                (39, 79000),
                (40, 76000),
                (41, 82000),
                (42, 85000),
                (43, 88000),
                (44, 92000),
                (45, 95000),
                (46, 98000),
                (47, 101000),
                (48, 104000),
                (49, 107000),
                (50, 110000)
      ]