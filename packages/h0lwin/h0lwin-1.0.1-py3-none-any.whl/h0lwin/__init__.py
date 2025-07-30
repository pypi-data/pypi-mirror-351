class H0lwin:
    def __init__(self):
        self.name = "H0lwin"
        self.age = 17
        self.country = "Iran"
        self.city = "Shiraz"
        self.married = True
        self.os = "Arch Linux"
        self.roles = ["Python Developer", "Frontend Developer"]
        self.languages = ["HTML", "CSS", "JavaScript", "Python", "React", "Next.js", "Tailwind", "Bash"]
        self.skills = ["Linux", "DevOps (intermediate)"]
        self.traits = ["Ambitious", "Hardworking", "Visionary"]
        self.orgs = ["Founder of Nullin & Neoplus", "Creator of the H0X Community"]
        self.interests = ["Technology", "Programming", "Music", "Bodybuilding"]
        self.links = {
            "GitHub": "https://github.com/heroinsh",
            "Instagram": "https://www.instagram.com/h0lwinum?igsh=MWU2eWI4dXBpOTllMA==",
            "Telegram": "https://t.me/H0lwin_P",
            "Location": "https://maps.app.goo.gl/TwpfCT3WtSAXKH6FA"
        }

    def get_full_info(self):
        return {
            "Name": self.name,
            "Age": self.age,
            "Country": self.country,
            "City": self.city,
            "Married": self.married,
            "OS": self.os,
            "Roles": self.roles,
            "Languages": self.languages,
            "Skills": self.skills,
            "Traits": self.traits,
            "Organizations": self.orgs,
            "Interests": self.interests,
            "SocialLinks": self.links
        }

    def get_languages(self):
        return self.languages

    def get_skills(self):
        return self.skills

    def get_social_links(self):
        return self.links

    def get_roles(self):
        return self.roles

    def get_location(self):
        return f"{self.city}, {self.country}"

    def is_married(self):
        return self.married
