import os

class Config:
    # This pulls the secret from your Railway Variables tab
    TOKEN = os.getenv("BOT_TOKEN") 
    
    # Your Section 8 Channel ID
    ANNOUNCEMENT_CHANNEL_ID = 1479327528723284019 
    
    # 0=Monday, 2=Wednesday, 4=Friday
    SCHEDULED_DAYS = [0, 2, 4]
    
    # Visuals
    EMBED_TITLE = "🏠 Section 8 Helper | Official Update"
    EMBED_COLOR = 0x2ECC71 
    FOOTER_TEXT = "Section 8 Assistant | Automated Housing Updates"