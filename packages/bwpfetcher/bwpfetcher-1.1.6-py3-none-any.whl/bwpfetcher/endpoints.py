from enum import Enum

class VoxylApiEndpoint(Enum):
    # Player
    PLAYER_INFO = "player/info/{uuid}"
    PLAYER_OVERALL = "player/stats/overall/{uuid}"
    PLAYER_GAME = "player/stats/game/{uuid}"
    PLAYER_STAT_RANKING = "player/ranking/{uuid}"
    PLAYER_GUILD = "player/guild/{uuid}"

    # Guild
    GUILD_INFO = "guild/info/{tag}"
    GUILD_INFO_ID = "guild/info/{id}"
    GUILD_MEMBERS = "guild/members/{tag}"
    GUILD_MEMBER_ID = "guild/members/{id}"
    GUILD_TOP = "guild/top"

    # Announcements
    ALL_ANNOUNCEMENTS = "announcement/all"

    # Leaderboards
    LEADERBOARD_NORMAL = "leaderboard/normal"
    LEADERBOARD_TECHNIQUE = "leaderboard/technique"
    LEADERBOARD_GAME = "leaderboard/game/{ref}"
    
    # Achievements 
    PLAYER_ACHIEVEMENTS = "achievements/player/{uuid}"
    ALL_ACHIEVEMENTS = "achievements/info"

    # Games
    GAME_INFO = "game/info/{game_uuid}"
    GAME_STATUS = "game/status/{game_uuid}"

    # Integration
    DISCORD_FROM_PLAYER = "integration/discord_from_player/{uuid}"
    PLAYER_FROM_DISCORD = "integration/player_from_discord/{discord_id}"
