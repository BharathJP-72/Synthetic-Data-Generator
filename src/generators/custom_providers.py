"""
Custom data providers for realistic synthetic data generation.
Extends Mimesis with domain-specific realistic data.
"""
import random
from typing import List


class CustomProviders:
    """Custom data providers for fields not well-covered by Mimesis."""
    
    # Realistic department names
    DEPARTMENTS = [
        "Sales", "Marketing", "Engineering", "Human Resources", "Finance",
        "Operations", "Customer Service", "IT", "Product Management",
        "Research & Development", "Legal", "Accounting", "Quality Assurance",
        "Business Development", "Administration", "Logistics", "Procurement",
        "Design", "Analytics", "Security", "Compliance", "Training"
    ]
    
    # Realistic product categories
    PRODUCT_CATEGORIES = [
        "Electronics", "Clothing", "Home & Garden", "Sports & Outdoors",
        "Books", "Toys & Games", "Health & Beauty", "Automotive",
        "Food & Beverage", "Office Supplies", "Pet Supplies", "Jewelry",
        "Tools & Hardware", "Music & Instruments", "Art & Crafts"
    ]
    
    # Realistic company names
    COMPANY_NAMES = [
        "TechCorp Solutions", "Global Innovations Inc", "Apex Industries",
        "Quantum Systems", "Stellar Enterprises", "Nexus Technologies",
        "Pinnacle Group", "Horizon Ventures", "Summit Corporation",
        "Vertex Solutions", "Catalyst Partners", "Fusion Dynamics",
        "Meridian Holdings", "Zenith Industries", "Atlas Corporation"
    ]
    
    # Realistic product names (tech/general)
    PRODUCT_NAMES = [
        "Wireless Mouse", "USB Cable", "Laptop Stand", "Phone Case",
        "Bluetooth Speaker", "Desk Lamp", "Notebook Set", "Water Bottle",
        "Backpack", "Headphones", "Keyboard", "Monitor", "Webcam",
        "Charging Cable", "Power Bank", "Screen Protector", "Stylus Pen",
        "Tablet Case", "External Hard Drive", "Flash Drive", "HDMI Cable"
    ]
    
    # Status values
    STATUS_VALUES = [
        "Active", "Inactive", "Pending", "Completed", "In Progress",
        "Approved", "Rejected", "On Hold", "Cancelled", "Delivered"
    ]
    
    @staticmethod
    def department() -> str:
        """Generate a realistic department name."""
        return random.choice(CustomProviders.DEPARTMENTS)
    
    @staticmethod
    def product_category() -> str:
        """Generate a realistic product category."""
        return random.choice(CustomProviders.PRODUCT_CATEGORIES)
    
    @staticmethod
    def company_name() -> str:
        """Generate a realistic company name."""
        return random.choice(CustomProviders.COMPANY_NAMES)
    
    @staticmethod
    def product_name() -> str:
        """Generate a realistic product name."""
"""
Custom data providers for realistic synthetic data generation.
Extends Mimesis with domain-specific realistic data.
"""
import random
from typing import List


class CustomProviders:
    """Custom data providers for fields not well-covered by Mimesis."""
    
    # Realistic department names
    DEPARTMENTS = [
        "Sales", "Marketing", "Engineering", "Human Resources", "Finance",
        "Operations", "Customer Service", "IT", "Product Management",
        "Research & Development", "Legal", "Accounting", "Quality Assurance",
        "Business Development", "Administration", "Logistics", "Procurement",
        "Design", "Analytics", "Security", "Compliance", "Training"
    ]
    
    # Realistic product categories
    PRODUCT_CATEGORIES = [
        "Electronics", "Clothing", "Home & Garden", "Sports & Outdoors",
        "Books", "Toys & Games", "Health & Beauty", "Automotive",
        "Food & Beverage", "Office Supplies", "Pet Supplies", "Jewelry",
        "Tools & Hardware", "Music & Instruments", "Art & Crafts"
    ]
    
    # Realistic company names
    COMPANY_NAMES = [
        "TechCorp Solutions", "Global Innovations Inc", "Apex Industries",
        "Quantum Systems", "Stellar Enterprises", "Nexus Technologies",
        "Pinnacle Group", "Horizon Ventures", "Summit Corporation",
        "Vertex Solutions", "Catalyst Partners", "Fusion Dynamics",
        "Meridian Holdings", "Zenith Industries", "Atlas Corporation"
    ]
    
    # Realistic product names (tech/general)
    PRODUCT_NAMES = [
        "Wireless Mouse", "USB Cable", "Laptop Stand", "Phone Case",
        "Bluetooth Speaker", "Desk Lamp", "Notebook Set", "Water Bottle",
        "Backpack", "Headphones", "Keyboard", "Monitor", "Webcam",
        "Charging Cable", "Power Bank", "Screen Protector", "Stylus Pen",
        "Tablet Case", "External Hard Drive", "Flash Drive", "HDMI Cable"
    ]
    
    # Status values
    STATUS_VALUES = [
        "Active", "Inactive", "Pending", "Completed", "In Progress",
        "Approved", "Rejected", "On Hold", "Cancelled", "Delivered"
    ]
    
    @staticmethod
    def department() -> str:
        """Generate a realistic department name."""
        return random.choice(CustomProviders.DEPARTMENTS)
    
    @staticmethod
    def product_category() -> str:
        """Generate a realistic product category."""
        return random.choice(CustomProviders.PRODUCT_CATEGORIES)
    
    @staticmethod
    def company_name() -> str:
        """Generate a realistic company name."""
        return random.choice(CustomProviders.COMPANY_NAMES)
    
    @staticmethod
    def product_name() -> str:
        """Generate a realistic product name."""
        return random.choice(CustomProviders.PRODUCT_NAMES)
    
    @staticmethod
    def status() -> str:
        """Generate a realistic status value."""
        return random.choice(CustomProviders.STATUS_VALUES)
    
    # Aliases for LLM compatibility
    @staticmethod
    def product() -> str:
        """Alias for product_name."""
        return CustomProviders.product_name()
    
    @staticmethod
    def company() -> str:
        """Alias for company_name."""
        return CustomProviders.company_name()
