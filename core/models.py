from django.db import models

# --------------------------------------------------
# Model to control signup branding elements per company
# Used to manage dynamic text and images on the signup page
# --------------------------------------------------
class SignupBranding(models.Model):
    # 🟠 Main bold title (e.g., "The best offer")
    title = models.CharField(max_length=100, default="The best offer")
    
    # 🔵 Subtitle below the title (e.g., "for your business")
    subtitle = models.CharField(max_length=100, default="for your business")
    
    # ⚪ Description paragraph (shown below subtitle)
    description = models.TextField(
        default="Join the Baobyte platform and take your projects to the next level. We care about security, style, and performance."
    )
    
    # 🖼️ Left image shown on the signup page (customizable per company)
    image = models.ImageField(upload_to='branding/', blank=True, null=True)

    def __str__(self):
        return f"Signup Branding: {self.title}"
